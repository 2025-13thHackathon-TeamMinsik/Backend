from django.shortcuts import render
from rest_framework import generics, permissions
from .models import EmployerReview, EmployeeReview
from .serializers import EmployerReviewSerializer, EmployeeReviewSerializer

# 사장 -> 대학생 평가
class EmployerReviewCreateView(generics.CreateAPIView):
    queryset = EmployerReview.objects.all()
    serializer_class = EmployerReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

# 대학생 후기 작성
class EmployeeReviewCreateView(generics.CreateAPIView):
    queryset = EmployeeReview.objects.all()
    serializer_class = EmployeeReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

# 공고별 대학생 후기 조회
class EmployeeReviewListView(generics.ListAPIView):
    serializer_class = EmployeeReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        job_id = self.kwargs.get('job_id')
        return EmployeeReview.objects.filter(job_id=job_id)

# 대학생별 사장 평가 조회 
class EmployerReviewListView(generics.ListAPIView):
    serializer_class = EmployerReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        employee_id = self.kwargs.get('employee_id')
        return EmployerReview.objects.filter(employee_id=employee_id)
