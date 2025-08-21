from django.urls import path
from .views import (
    JobPostListView, JobPostDetailView,
    JobPostCreateView, JobPostUpdateView,JobPostLikeToggleView, JobPostDeleteView, 
    JobPostHistoryView,JobPostSearchListView, ApplicationView, AcceptApplicationView
)

app_name = 'jobs'

urlpatterns = [
    # 전체 공고 조회
    path('posts/', JobPostListView.as_view(), name='post-list'),

    # 공고 상세 조회
    path('posts/<int:pk>/', JobPostDetailView.as_view(), name='post-detail'),

    # 공고 작성
    path('posts/create/', JobPostCreateView.as_view(), name='post-create'),

    # 공고 수정
    path('posts/<int:pk>/update/', JobPostUpdateView.as_view(), name='post-update'),

    # 공고 삭제
    path('posts/<int:pk>/delete/', JobPostDeleteView.as_view(), name='post-delete'),

    # 공고 이력 조회
    path('posts/history/', JobPostHistoryView.as_view(), name='post-history'),
    # 공고 내역 검색
    path('search/', JobPostSearchListView.as_view(), name='jobpost-search'),
    # 공고 좋아요 
    path('<int:pk>/like/', JobPostLikeToggleView.as_view(), name='jobpost-like'),
    # 학생의 공고 지원
    path('applications/<int:job_id>/', ApplicationView.as_view(), name='apply_job'),
    # 소상공인의 수락/거절
    path('applications/<int:application_id>/respond/', AcceptApplicationView.as_view(), name='accept_application'),

]
