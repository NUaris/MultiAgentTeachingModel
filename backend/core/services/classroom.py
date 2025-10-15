"""
Classroom Agent Service
负责班级数据聚合、个性化增量方案生成
"""
import logging
from typing import Dict, List, Any, Optional
from django.db.models import Avg, Count, Q
from ..openai_utils import get_openai_client
from ..models import (
    TeacherOutline, 
    UnifiedLessonPlan,
    PersonalizationDelta,
    Attempt,
    Student
)

logger = logging.getLogger(__name__)


class ClassroomAgent:
    """
    Classroom Agent: 班级管理与个性化智能体
    
    职责:
    - 聚合全班答题数据
    - 生成班级统计报告
    - 在统一计划基础上生成个性化增量
    - 输出学生分组与个性化方案
    """
    
    def __init__(self):
        self.client = get_openai_client()
        self.model = "gpt-4o-mini"
        self.temperature = 0.7
    
    def aggregate_class_data(
        self,
        outline: TeacherOutline,
        lesson_plan: Optional[UnifiedLessonPlan] = None
    ) -> PersonalizationDelta:
        """
        聚合班级数据,生成个性化方案
        
        Args:
            outline: 教学大纲
            lesson_plan: 统一教学计划(基线)
        
        Returns:
            个性化增量对象
        """
        logger.info(f"🎯 Classroom Agent: Aggregating data for '{outline.title}'")
        
        # 获取所有已完成的答题会话
        completed_attempts = Attempt.objects.filter(
            outline=outline,
            is_completed=True
        ).select_related('student').prefetch_related('answers')
        
        if not completed_attempts.exists():
            logger.warning("⚠️ No completed attempts found")
            return self._create_empty_delta(outline, lesson_plan)
        
        # 计算班级统计
        class_summary = self._calculate_class_summary(completed_attempts)
        
        # 生成学生个性化报告
        student_reports = self._generate_student_reports(completed_attempts)
        
        # 生成个性化增量方案
        plan_delta = self._generate_plan_delta(class_summary, lesson_plan)
        
        # 保存到数据库
        personalization = PersonalizationDelta.objects.create(
            outline=outline,
            lesson_plan=lesson_plan,
            class_summary=class_summary,
            plan_delta=plan_delta,
            student_reports=student_reports,
            is_published=False
        )
        
        logger.info(f"✅ Personalization delta created (ID: {personalization.id})")
        return personalization
    
    def publish_plan(
        self,
        personalization_id: int,
        reviewed_by_user=None
    ) -> PersonalizationDelta:
        """
        教师审核并发布个性化方案
        
        Args:
            personalization_id: 个性化方案 ID
            reviewed_by_user: 审核教师
        
        Returns:
            已发布的个性化方案
        """
        from django.utils import timezone
        
        personalization = PersonalizationDelta.objects.get(id=personalization_id)
        personalization.is_published = True
        personalization.reviewed_by = reviewed_by_user
        personalization.published_at = timezone.now()
        personalization.save()
        
        logger.info(f"✅ Personalization plan published (ID: {personalization_id})")
        return personalization
    
    def _calculate_class_summary(self, attempts) -> Dict[str, Any]:
        """计算班级统计数据"""
        total_students = attempts.values('student').distinct().count()
        
        # 计算平均正确率和用时
        correct_answers = 0
        total_answers = 0
        total_time = 0.0
        
        for attempt in attempts:
            for answer in attempt.answers.all():
                total_answers += 1
                if answer.is_correct:
                    correct_answers += 1
                total_time += answer.time_spent_sec
        
        accuracy_avg = correct_answers / total_answers if total_answers > 0 else 0.0
        time_avg_sec = total_time / total_answers if total_answers > 0 else 0.0
        
        return {
            'total_students': total_students,
            'accuracy_avg': round(accuracy_avg, 2),
            'time_avg_sec': round(time_avg_sec, 2),
            'total_answers': total_answers
        }
    
    def _generate_student_reports(self, attempts) -> List[Dict[str, Any]]:
        """生成学生个性化报告"""
        reports = []
        
        for attempt in attempts:
            student = attempt.student
            correct_count = attempt.answers.filter(is_correct=True).count()
            total_count = attempt.answers.count()
            accuracy = correct_count / total_count if total_count > 0 else 0.0
            
            # TODO: 在里程碑 6 使用 LLM 生成更详细的报告
            reports.append({
                'student_id': student.student_id,
                'name': student.name,
                'accuracy': round(accuracy, 2),
                'status': self._classify_student(accuracy)
            })
        
        return reports
    
    def _generate_plan_delta(
        self,
        class_summary: Dict[str, Any],
        lesson_plan: Optional[UnifiedLessonPlan]
    ) -> Dict[str, Any]:
        """
        生成个性化增量方案
        TODO: 在里程碑 6 使用 LLM 基于班级数据生成增量
        """
        avg_accuracy = class_summary.get('accuracy_avg', 0.0)
        
        # 占位逻辑:根据班级平均水平调整
        delta = {
            'group_overrides': [],
            'additional_activities': [],
            'time_adjustments': {}
        }
        
        if avg_accuracy < 0.6:
            delta['group_overrides'].append({
                'group': 'low',
                'action': '增加基础练习时间',
                'minutes': 10
            })
        elif avg_accuracy > 0.85:
            delta['group_overrides'].append({
                'group': 'high',
                'action': '增加挑战题目',
                'minutes': 5
            })
        
        return delta
    
    def _classify_student(self, accuracy: float) -> str:
        """学生水平分类"""
        if accuracy >= 0.85:
            return 'high'
        elif accuracy >= 0.6:
            return 'medium'
        else:
            return 'low'
    
    def _create_empty_delta(
        self,
        outline: TeacherOutline,
        lesson_plan: Optional[UnifiedLessonPlan]
    ) -> PersonalizationDelta:
        """创建空的个性化方案(无数据时)"""
        return PersonalizationDelta.objects.create(
            outline=outline,
            lesson_plan=lesson_plan,
            class_summary={'total_students': 0},
            plan_delta={},
            student_reports=[],
            is_published=False
        )
