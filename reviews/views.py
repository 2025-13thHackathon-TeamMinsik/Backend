from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from .models import EmployerReview, EmployeeReview
from .serializers import EmployerReviewSerializer, EmployeeReviewSerializer
from matching.models import MatchRequest


# 사장이 대학생을 평가
class EmployerReviewCreateView(generics.CreateAPIView):
    queryset = EmployerReview.objects.all()
    serializer_class = EmployerReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        job = serializer.validated_data['job']
        match = MatchRequest.objects.filter(job_post=job, status='matched').first()
        if not match:
            raise ValidationError("이 공고에는 아직 매칭 완료된 대학생이 없습니다.")
        serializer.save(author=self.request.user, employee=match.helper)


# 대학생이 사장을 평가
class EmployeeReviewCreateView(generics.CreateAPIView):
    queryset = EmployeeReview.objects.all()
    serializer_class = EmployeeReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        job = serializer.validated_data['job']
        helper = self.request.user

        if EmployeeReview.objects.filter(author=helper, job=job).exists():
            raise ValidationError("이미 이 공고에 대한 리뷰를 작성하셨습니다.")

        match = MatchRequest.objects.filter(job_post=job, helper=helper, status='matched').first()
        if not match:
            raise ValidationError("아직 매칭 완료된 사장이 없습니다.")

        if not EmployerReview.objects.filter(employee=helper, job=job).exists():
            raise ValidationError("소상공인이 먼저 리뷰를 작성해야 대학생이 리뷰를 작성할 수 있습니다.")

        serializer.save(author=helper, employer=match.employer)

# 공고별 대학생 후기 조회
class EmployeeReviewListView(generics.ListAPIView):
    serializer_class = EmployeeReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        job_id = self.kwargs.get('job_id')
        return EmployeeReview.objects.filter(job_id=job_id)


# 특정 대학생이 받은 사장 평가 조회
class EmployerReviewListView(generics.ListAPIView):
    serializer_class = EmployerReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        employee_id = self.kwargs.get('employee_id')
        return EmployerReview.objects.filter(employee_id=employee_id)
