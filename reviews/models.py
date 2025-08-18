from django.db import models
from django.conf import settings
from jobs.models import JobPost

class EmployerReview(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employer_reviews')
    job = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='employer_reviews')

    participation = models.PositiveSmallIntegerField() #참여도
    diligence = models.PositiveSmallIntegerField()  #성실함
    punctuality = models.PositiveSmallIntegerField() #시간준수
    cheerful_attitude = models.PositiveSmallIntegerField()  #밝은태도
    politeness = models.PositiveSmallIntegerField()  #예의바름
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('employee', 'job')  # 공고당 한 번만 평가 가능

class EmployeeReview(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee_reviews')
    job = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='employee_reviews')
    
    rating = models.PositiveSmallIntegerField()
    content = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('employee', 'job')  # 공고당 한 번만 후기 작성 가능
