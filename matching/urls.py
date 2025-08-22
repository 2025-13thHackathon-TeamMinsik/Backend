from django.urls import path
from . import views

urlpatterns = [
    # 소상공인 → 추천 학생 요청
    path('request/', views.MatchRequestView.as_view(), name='request_helper'),
    # 학생 -> 소상공인의 요청 수락/거절
    path('request/<int:request_id>/student-respond/', views.StudentRespondMatchRequestView.as_view(), name='student_respond_match_request'),
    # 추천 공고
    path('recommended/jobs/', views.RecommendJobsView.as_view(), name='recommend-jobs'),
    # 추천 학생
    path('recommended/students/', views.RecommendStudentsView.as_view(), name='recommend-students'),
]