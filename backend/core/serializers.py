"""
Core Serializers for API
"""
from rest_framework import serializers
from .models import (
    TeacherOutline,
    UnifiedLessonPlan,
    QuizQuestion,
    Student,
    Attempt,
    AttemptAnswer,
    PersonalizationDelta
)


class TeacherOutlineSerializer(serializers.ModelSerializer):
    """教学大纲序列化器"""
    class Meta:
        model = TeacherOutline
        fields = ['id', 'title', 'content', 'duration_min', 'difficulty', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class UnifiedLessonPlanSerializer(serializers.ModelSerializer):
    """统一教学计划序列化器"""
    class Meta:
        model = UnifiedLessonPlan
        fields = ['id', 'outline', 'version', 'objectives', 'sequence', 
                  'activities', 'checks', 'created_at']
        read_only_fields = ['id', 'created_at']


class QuizQuestionSerializer(serializers.ModelSerializer):
    """题目序列化器"""
    class Meta:
        model = QuizQuestion
        fields = ['id', 'outline', 'question_text', 'question_type', 'options',
                  'correct_answer', 'explanation', 'difficulty', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']


class StudentSerializer(serializers.ModelSerializer):
    """学生序列化器"""
    class Meta:
        model = Student
        fields = ['id', 'student_id', 'name', 'grade', 'class_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class AttemptAnswerSerializer(serializers.ModelSerializer):
    """答题记录序列化器"""
    class Meta:
        model = AttemptAnswer
        fields = ['id', 'attempt', 'question', 'student_answer', 'is_correct',
                  'time_spent_sec', 'feedback', 'answered_at']
        read_only_fields = ['id', 'answered_at']


class AttemptSerializer(serializers.ModelSerializer):
    """答题会话序列化器"""
    answers = AttemptAnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Attempt
        fields = ['id', 'student', 'outline', 'started_at', 'completed_at',
                  'total_score', 'is_completed', 'answers']
        read_only_fields = ['id', 'started_at']


class PersonalizationDeltaSerializer(serializers.ModelSerializer):
    """个性化方案序列化器"""
    class Meta:
        model = PersonalizationDelta
        fields = ['id', 'outline', 'lesson_plan', 'class_summary', 'plan_delta',
                  'student_reports', 'is_published', 'reviewed_by', 'created_at', 
                  'published_at']
        read_only_fields = ['id', 'created_at']
