from django.db import models
from django.conf import settings
from jobs.models import JobPost


# 사장이 대학생을 평가
class EmployerReview(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='written_employer_reviews',
    )
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_employer_reviews',
    )
    job = models.ForeignKey(
        JobPost,
        on_delete=models.CASCADE,
        related_name='employer_reviews',
    )
    participation = models.PositiveSmallIntegerField()
    diligence = models.PositiveSmallIntegerField()
    punctuality = models.PositiveSmallIntegerField()
    cheerful_attitude = models.PositiveSmallIntegerField()
    politeness = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=True) 

    class Meta:
        unique_together = ('employee', 'job')


# 대학생이 사장을 평가
class EmployeeReview(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='written_employee_reviews',
    )
    employer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_employee_reviews',
    )
    job = models.ForeignKey(
        JobPost,
        on_delete=models.CASCADE,
        related_name='employee_reviews'
    )
    rating = models.PositiveSmallIntegerField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=True)

    class Meta:
        unique_together = ('author', 'job')
