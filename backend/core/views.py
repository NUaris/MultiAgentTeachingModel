"""
Core API Views
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


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
