from django.db import models
from django.conf import settings
from jobs.models import JobPost
User = settings.AUTH_USER_MODEL

# Create your models here.

# 소상공인 -> 추천 대학생
class MatchRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', '대기'),
        ('accepted', '수락'),
        ('rejected', '거절'),
        ('matched', '매칭완료'),
        ('completed', '작업완료'),
    ]

    # 요청 보낸 소상공인
    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_requests")
    # 요청 받은 학생
    helper = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_requests")
    # 어떤 공고
    job_post = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name="match_requests")
    # 요청 진행 상태
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    # 요청 시각
    created_at = models.DateTimeField(auto_now_add=True)

# 추천 공고
class RecommendedJobPost(models.Model):
    job_post = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='recommended_job_posts')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommended_job_posts')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job_post', 'student')  # 중복 방지

# 추천 대학생
class RecommendedStudent(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations_from_jobs')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommended_students')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('owner', 'student')  # 같은 소상공인에게 동일 학생 추천 방지
        ordering = ['-created_at']