from django.urls import path
from . import views

urlpatterns = [
    # 공고와 지원자 리스트 조회
    path('my-jobs/', views.JobAndApplicantsListView.as_view(), name='my_jobs_list'),
    # 지원자 상세 정보 조회
    path('applications/<int:application_id>/detail/', views.StudentDetailView.as_view(), name='student_detail'),
    # 재능 요청하기
    # path('request-talent/', views.request_talent, name='request_talent'),
]