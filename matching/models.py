from django.db import models
from django.conf import settings
from jobs.models import JobPost
User = settings.AUTH_USER_MODEL

# Create your models here.

# 대학생에게 재능 요청하기
class TalentRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', '대기'),
        ('accepted', '수락'),
        ('rejected', '거절'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests_received')
    job_post = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='requests_sent')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests_created')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'job_post')

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
    job_post = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='recommended_for_students')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job_post', 'student')  # 중복 방지