"""
Django Admin Configuration
"""
from django.contrib import admin
from .models import (
    TeacherOutline,
    UnifiedLessonPlan,
    QuizQuestion,
    Student,
    Attempt,
    AttemptAnswer,
    PersonalizationDelta
)


@admin.register(TeacherOutline)
class TeacherOutlineAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'difficulty', 'duration_min', 'created_at']
    list_filter = ['difficulty', 'created_at']
    search_fields = ['title', 'content']


@admin.register(UnifiedLessonPlan)
class UnifiedLessonPlanAdmin(admin.ModelAdmin):
    list_display = ['id', 'outline', 'version', 'created_at']
    list_filter = ['created_at']
    search_fields = ['outline__title', 'version']


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'outline', 'question_type', 'difficulty', 'order', 'created_at']
    list_filter = ['question_type', 'difficulty', 'created_at']
    search_fields = ['question_text', 'outline__title']
    ordering = ['outline', 'order']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'student_id', 'name', 'grade', 'class_name', 'created_at']
    list_filter = ['grade', 'class_name']
    search_fields = ['student_id', 'name']


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'outline', 'total_score', 'is_completed', 'started_at']
    list_filter = ['is_completed', 'started_at']
    search_fields = ['student__student_id', 'student__name', 'outline__title']


@admin.register(AttemptAnswer)
class AttemptAnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'attempt', 'question', 'is_correct', 'time_spent_sec', 'answered_at']
    list_filter = ['is_correct', 'answered_at']
    search_fields = ['attempt__student__student_id', 'question__question_text']


@admin.register(PersonalizationDelta)
class PersonalizationDeltaAdmin(admin.ModelAdmin):
    list_display = ['id', 'outline', 'is_published', 'reviewed_by', 'created_at']
    list_filter = ['is_published', 'created_at']
    search_fields = ['outline__title']

