"""
Tutor Agent Service
负责出题、批改、生成个体反馈
"""
import logging
from typing import Dict, List, Any, Optional
from ..openai_utils import get_openai_client
from ..models import TeacherOutline, QuizQuestion, Attempt, AttemptAnswer, Student

logger = logging.getLogger(__name__)


class TutorAgent:
    """
    Tutor Agent: 个性化辅导智能体
    
    职责:
    - 根据大纲生成题目
    - 自动批改学生答案
    - 生成个体反馈报告(含用时分析)
    """
    
    def __init__(self):
        self.client = get_openai_client()
        self.model = "gpt-4o-mini"
        self.temperature = 0.7
    
    def generate_quiz(
        self,
        outline: TeacherOutline,
        num_questions: int = 5,
        difficulty: Optional[str] = None
    ) -> List[QuizQuestion]:
        """
        为指定大纲生成题目
        
        Args:
            outline: 教学大纲
            num_questions: 题目数量
            difficulty: 难度(如未指定,使用大纲难度)
        
        Returns:
            生成的题目列表
        """
        logger.info(f"📝 Tutor Agent: Generating {num_questions} questions for '{outline.title}'")
        
        difficulty = difficulty or outline.difficulty
        
        # TODO: 在里程碑 6 实现完整的题目生成逻辑
        # 目前返回占位数据
        questions = []
        for i in range(num_questions):
            question = QuizQuestion.objects.create(
                outline=outline,
                question_text=f"示例题目 {i+1} (待生成)",
                question_type='multiple_choice',
                options=['A', 'B', 'C', 'D'],
                correct_answer='A',
                explanation='占位解析',
                difficulty=difficulty,
                order=i + 1
            )
            questions.append(question)
        
        logger.info(f"✅ Generated {len(questions)} questions")
        return questions
    
    def grade_answer(
        self,
        question: QuizQuestion,
        student_answer: str
    ) -> Dict[str, Any]:
        """
        批改单个答案
        
        Args:
            question: 题目对象
            student_answer: 学生答案
        
        Returns:
            批改结果 {is_correct, feedback}
        """
        logger.info(f"✍️ Grading answer for question {question.id}")
        
        # TODO: 在里程碑 6 实现基于 LLM 的智能批改
        # 目前使用简单字符串比较
        is_correct = student_answer.strip().lower() == question.correct_answer.strip().lower()
        
        feedback = "答案正确!" if is_correct else f"答案错误。正确答案是: {question.correct_answer}"
        
        return {
            'is_correct': is_correct,
            'feedback': feedback
        }
    
    def generate_individual_feedback(
        self,
        outline: TeacherOutline,
        student: Student
    ) -> Dict[str, Any]:
        """
        生成学生个体反馈报告
        
        Args:
            outline: 教学大纲
            student: 学生对象
        
        Returns:
            反馈报告 {summary, items, recommendations}
        """
        logger.info(f"📊 Generating feedback for student {student.student_id}")
        
        # 查询学生的答题记录
        attempts = Attempt.objects.filter(
            student=student,
            outline=outline,
            is_completed=True
        ).prefetch_related('answers')
        
        if not attempts.exists():
            return {
                'student_id': student.student_id,
                'outline_id': outline.id,
                'summary': {'total': 0, 'correct': 0, 'accuracy': 0.0},
                'items': [],
                'recommendations': ['尚未完成任何答题']
            }
        
        # 统计数据
        total_questions = 0
        correct_count = 0
        items = []
        
        for attempt in attempts:
            for answer in attempt.answers.all():
                total_questions += 1
                if answer.is_correct:
                    correct_count += 1
                
                items.append({
                    'qid': f"Q{answer.question.order}",
                    'correct': 1 if answer.is_correct else 0,
                    'time_sec': answer.time_spent_sec
                })
        
        accuracy = correct_count / total_questions if total_questions > 0 else 0.0
        
        # TODO: 在里程碑 6 使用 LLM 生成个性化建议
        recommendations = self._generate_recommendations(accuracy)
        
        return {
            'student_id': student.student_id,
            'outline_id': outline.id,
            'summary': {
                'total': total_questions,
                'correct': correct_count,
                'accuracy': round(accuracy, 2)
            },
            'items': items,
            'recommendations': recommendations
        }
    
    def _generate_recommendations(self, accuracy: float) -> List[str]:
        """生成学习建议(占位逻辑)"""
        if accuracy >= 0.9:
            return ['表现优秀!可以挑战更高难度题目。']
        elif accuracy >= 0.7:
            return ['基础扎实,建议复习错题。']
        else:
            return ['需要加强基础练习,建议重新学习相关知识点。']
