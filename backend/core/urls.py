"""
Core App URL Configuration
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # 健康检查
    path('health/', views.health_check, name='health_check'),
    
    # 教学大纲
    path('outline/', views.create_outline, name='create_outline'),
    path('outline/<int:outline_id>/', views.get_outline, name='get_outline'),
    path('outlines/', views.list_outlines, name='list_outlines'),
    
    # Teacher Agent
    path('teacher_agent/plan/<int:outline_id>/', views.generate_lesson_plan, name='generate_lesson_plan'),
    
    # Tutor Agent
    path('tutor/quiz/<int:outline_id>/', views.generate_quiz, name='generate_quiz'),
    path('submit_answer/', views.submit_answer, name='submit_answer'),
    path('feedback/<int:outline_id>/<str:student_id>/', views.get_feedback, name='get_feedback'),
    
    # Classroom Agent
    path('classroom/aggregate/<int:outline_id>/', views.aggregate_class_data, name='aggregate_class_data'),
    path('classroom/publish/<int:outline_id>/', views.publish_plan, name='publish_plan'),
    
    # 学生相关
    path('student/', views.create_student, name='create_student'),
    path('attempt/', views.create_attempt, name='create_attempt'),
]

