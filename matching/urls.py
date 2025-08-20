from django.urls import path
from . import views

urlpatterns = [
    # 추천 공고
    path('recommended/jobs/<int:student_id>', views.RecommendJobsView.as_view(), name='recommend-jobs'),
    # 추천 학생
    path('recommended/students/<int:job_id>/', views.RecommendStudentsView.as_view(), name='recommend-students'),
]