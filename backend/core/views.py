"""
Core API Views
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import TeacherOutline, QuizQuestion, Student, Attempt, AttemptAnswer
from .serializers import (
    TeacherOutlineSerializer,
    QuizQuestionSerializer,
    StudentSerializer,
    AttemptSerializer,
    AttemptAnswerSerializer
)
from .services import TeacherAgent, TutorAgent, ClassroomAgent


@api_view(['GET'])
def health_check(request):
    """
    健康检查端点
    GET /api/health/
    """
    return Response({
        'status': 'ok',
        'message': 'AI Education System API is running',
        'version': '1.0.0'
    }, status=status.HTTP_200_OK)


# ============ 教学大纲相关 ============

@api_view(['POST'])
def create_outline(request):
    """
    创建教学大纲
    POST /api/outline/
    """
    serializer = TeacherOutlineSerializer(data=request.data)
    if serializer.is_valid():
        outline = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_outline(request, outline_id):
    """
    获取教学大纲及相关题目
    GET /api/outline/{outline_id}/
    """
    try:
        outline = TeacherOutline.objects.get(id=outline_id)
        questions = QuizQuestion.objects.filter(outline=outline)
        
        return Response({
            'outline': TeacherOutlineSerializer(outline).data,
            'questions': QuizQuestionSerializer(questions, many=True).data
        })
    except TeacherOutline.DoesNotExist:
        return Response({'error': 'Outline not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def list_outlines(request):
    """
    获取所有教学大纲列表
    GET /api/outlines/
    """
    outlines = TeacherOutline.objects.all()
    serializer = TeacherOutlineSerializer(outlines, many=True)
    return Response(serializer.data)


# ============ Teacher Agent 相关 ============

@api_view(['POST'])
def generate_lesson_plan(request, outline_id):
    """
    生成统一教学计划 (Teacher Agent)
    POST /api/teacher_agent/plan/{outline_id}/
    """
    try:
        outline = TeacherOutline.objects.get(id=outline_id)
        agent = TeacherAgent()
        
        # 调用 Teacher Agent 生成计划
        lesson_plan = agent.generate_lesson_plan(outline)
        
        return Response({
            'message': 'Lesson plan generated successfully',
            'plan_id': lesson_plan.id,
            'version': lesson_plan.version
        }, status=status.HTTP_201_CREATED)
    except TeacherOutline.DoesNotExist:
        return Response({'error': 'Outline not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============ Tutor Agent 相关 ============

@api_view(['POST'])
def generate_quiz(request, outline_id):
    """
    生成题目 (Tutor Agent)
    POST /api/tutor/quiz/{outline_id}/
    """
    try:
        outline = TeacherOutline.objects.get(id=outline_id)
        num_questions = request.data.get('num_questions', 5)
        
        agent = TutorAgent()
        questions = agent.generate_quiz(outline, num_questions=num_questions)
        
        return Response({
            'message': f'{len(questions)} questions generated',
            'questions': QuizQuestionSerializer(questions, many=True).data
        }, status=status.HTTP_201_CREATED)
    except TeacherOutline.DoesNotExist:
        return Response({'error': 'Outline not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def submit_answer(request):
    """
    提交学生答案
    POST /api/submit_answer/
    
    Body: {
        "attempt_id": 1,
        "question_id": 1,
        "student_answer": "A",
        "time_spent_sec": 8.5
    }
    """
    attempt_id = request.data.get('attempt_id')
    question_id = request.data.get('question_id')
    student_answer = request.data.get('student_answer')
    time_spent_sec = request.data.get('time_spent_sec', 0.0)
    
    try:
        attempt = Attempt.objects.get(id=attempt_id)
        question = QuizQuestion.objects.get(id=question_id)
        
        # 使用 Tutor Agent 批改
        agent = TutorAgent()
        result = agent.grade_answer(question, student_answer)
        
        # 保存答题记录
        answer = AttemptAnswer.objects.create(
            attempt=attempt,
            question=question,
            student_answer=student_answer,
            is_correct=result['is_correct'],
            time_spent_sec=time_spent_sec,
            feedback=result['feedback']
        )
        
        return Response({
            'is_correct': result['is_correct'],
            'feedback': result['feedback']
        }, status=status.HTTP_201_CREATED)
    except (Attempt.DoesNotExist, QuizQuestion.DoesNotExist) as e:
        return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_feedback(request, outline_id, student_id):
    """
    获取学生个体反馈
    GET /api/feedback/{outline_id}/{student_id}/
    """
    try:
        outline = TeacherOutline.objects.get(id=outline_id)
        student = Student.objects.get(student_id=student_id)
        
        agent = TutorAgent()
        feedback = agent.generate_individual_feedback(outline, student)
        
        return Response(feedback)
    except (TeacherOutline.DoesNotExist, Student.DoesNotExist) as e:
        return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)


# ============ Classroom Agent 相关 ============

@api_view(['POST'])
def aggregate_class_data(request, outline_id):
    """
    聚合班级数据并生成个性化方案 (Classroom Agent)
    POST /api/classroom/aggregate/{outline_id}/
    """
    try:
        outline = TeacherOutline.objects.get(id=outline_id)
        agent = ClassroomAgent()
        
        personalization = agent.aggregate_class_data(outline)
        
        return Response({
            'personalization_id': personalization.id,
            'class_summary': personalization.class_summary,
            'plan_delta': personalization.plan_delta,
            'student_reports': personalization.student_reports
        }, status=status.HTTP_201_CREATED)
    except TeacherOutline.DoesNotExist:
        return Response({'error': 'Outline not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def publish_plan(request, outline_id):
    """
    教师审核并发布个性化方案
    POST /api/classroom/publish/{outline_id}/
    
    Body: {"personalization_id": 1}
    """
    personalization_id = request.data.get('personalization_id')
    
    try:
        agent = ClassroomAgent()
        personalization = agent.publish_plan(personalization_id)
        
        return Response({
            'message': 'Plan published successfully',
            'personalization_id': personalization.id,
            'published_at': personalization.published_at
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)


# ============ 学生相关 ============

@api_view(['POST'])
def create_student(request):
    """
    创建学生
    POST /api/student/
    """
    serializer = StudentSerializer(data=request.data)
    if serializer.is_valid():
        student = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_attempt(request):
    """
    创建答题会话
    POST /api/attempt/
    
    Body: {"student_id": "S001", "outline_id": 1}
    """
    student_id = request.data.get('student_id')
    outline_id = request.data.get('outline_id')
    
    try:
        student = Student.objects.get(student_id=student_id)
        outline = TeacherOutline.objects.get(id=outline_id)
        
        attempt = Attempt.objects.create(student=student, outline=outline)
        return Response({
            'attempt_id': attempt.id,
            'student_id': student.student_id,
            'outline_id': outline.id
        }, status=status.HTTP_201_CREATED)
    except (Student.DoesNotExist, TeacherOutline.DoesNotExist) as e:
        return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

