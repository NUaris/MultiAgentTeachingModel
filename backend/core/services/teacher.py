"""
Teacher Agent Service
负责生成统一教学计划(Unified Lesson Plan)
"""
import logging
from typing import Dict, List, Any, Optional
from ..openai_utils import get_openai_client
from ..models import TeacherOutline, UnifiedLessonPlan

logger = logging.getLogger(__name__)


class TeacherAgent:
    """
    Teacher Agent: 根据教学大纲生成统一教学计划
    
    职责:
    - 分析教学大纲内容
    - 生成教学目标(objectives)
    - 设计知识点序列(sequence)
    - 规划教学活动(activities)
    - 设置检查点(checks)
    """
    
    def __init__(self):
        self.client = get_openai_client()
        self.model = "gpt-4o-mini"
        self.temperature = 0.7
    
    def generate_lesson_plan(
        self, 
        outline: TeacherOutline,
        version: str = "v1.0"
    ) -> UnifiedLessonPlan:
        """
        为指定教学大纲生成统一教学计划
        
        Args:
            outline: 教学大纲对象
            version: 版本号
        
        Returns:
            生成的教学计划对象
        """
        logger.info(f"🎓 Teacher Agent: Generating lesson plan for '{outline.title}'")
        
        # 构建 Prompt
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(outline)
        
        try:
            # 调用 OpenAI API
            response = self.client.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                temperature=self.temperature,
                max_tokens=2000
            )
            
            # 解析响应并保存(TODO: 在里程碑 6 实现完整逻辑)
            plan_data = self._parse_response(response['content'])
            
            # 创建教学计划对象
            lesson_plan = UnifiedLessonPlan.objects.create(
                outline=outline,
                version=version,
                objectives=plan_data.get('objectives', []),
                sequence=plan_data.get('sequence', []),
                activities=plan_data.get('activities', []),
                checks=plan_data.get('checks', [])
            )
            
            logger.info(f"✅ Lesson plan created successfully (ID: {lesson_plan.id})")
            return lesson_plan
            
        except Exception as e:
            logger.error(f"❌ Failed to generate lesson plan: {str(e)}")
            raise
    
    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        return """你是一位资深教学设计专家,擅长根据教学大纲制定结构化的教学计划。

你的任务是分析教学大纲,生成包含以下内容的统一教学计划:
1. objectives: 教学目标列表(3-5个明确目标)
2. sequence: 知识点序列(按教学顺序)
3. activities: 教学活动列表(包含活动ID、标题、时长)
4. checks: 检查点列表(用于评估学习进度)

请以 JSON 格式输出,确保结构清晰、逻辑连贯。"""
    
    def _build_user_prompt(self, outline: TeacherOutline) -> str:
        """构建用户提示词"""
        return f"""教学大纲信息:
- 标题: {outline.title}
- 难度: {outline.difficulty}
- 课时长度: {outline.duration_min} 分钟
- 大纲内容:
{outline.content}

请为此大纲生成统一教学计划(JSON 格式)。"""
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        解析 AI 响应
        TODO: 在里程碑 6 实现完整的 JSON 解析与验证
        """
        import json
        import re
        
        # 尝试提取 JSON
        try:
            # 移除 Markdown 代码块标记
            cleaned = re.sub(r'```json\s*|\s*```', '', response_text)
            return json.loads(cleaned.strip())
        except json.JSONDecodeError:
            logger.warning("⚠️ Failed to parse JSON, using fallback structure")
            return {
                'objectives': ['分析大纲内容', '理解核心概念'],
                'sequence': ['引入', '讲解', '练习'],
                'activities': [
                    {'id': 'A1', 'title': '引入示例', 'minutes': 5},
                    {'id': 'A2', 'title': '核心讲解', 'minutes': 15}
                ],
                'checks': []
            }
