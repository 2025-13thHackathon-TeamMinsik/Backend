from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Prefetch, Avg
from django.utils import timezone

from jobs.models import JobPost, Application
from accounts.models import User
from reviews.models import EmployerReview
from .serializers import (
    JobAndRequestedSerializer,
    StudentDetailSerializer,
)

# Create your views here.

# 소상공인이 올린 공고와 지원자 리스트 조회
class JobAndApplicantsListView(generics.ListAPIView):
    serializer_class = JobAndRequestedSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 로그인한 소상공인의 공고만 조회
        return JobPost.objects.filter(
            owner = self.request.user
        ).prefetch_related(
            Prefetch(
                'applications',
                queryset = Application.objects.select_related(
                    'applicant', 
                    'applicant__profile',
                    'applicant__portfolio'
                )
            )
        ).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        # 소상공인 권한 확인
        if not (hasattr(request.user, 'profile') and request.user.profile.role == 'owner'):
            return Response(
                {'error': '소상공인만 접근 가능합니다.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().list(request, *args, **kwargs)

# 지원자 상세 정보 조회
class StudentDetailView(generics.RetrieveAPIView):
    serializer_class = StudentDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # 소상공인 권한 확인
        if not (hasattr(self.request.user, 'profile') and self.request.user.profile.role == 'owner'):
            raise PermissionError('소상공인만 접근 가능합니다.')
        
        application_id = self.kwargs.get('application_id')
        # 자신의 공고에 지원한 신청서만 조회 가능
        return get_object_or_404(
            Application.objects.select_related(
                'applicant', 
                'applicant__profile', 
                'applicant__portfolio',
                'job_post'
            ),
            id=application_id,
            job_post__owner=self.request.user
        )
    
    def handle_exception(self, exc):
        if isinstance(exc, PermissionError):
            return Response(
                {'error': str(exc)}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().handle_exception(exc)

# 재능 요청하기

