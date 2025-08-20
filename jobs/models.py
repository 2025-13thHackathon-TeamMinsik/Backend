from django.db import models
from django.conf import settings

class JobPost(models.Model):
    PAYMENT_CHOICES = [
        ('LOCAL_CURRENCY', '지역화폐'),
        ('VOLUNTEER_TIME', '봉사시간'),
    ]
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_posts'
    )
    duration_time = models.CharField(
        max_length=100,
        help_text='예: "월/수 4시간, 1달" - 사용자가 한 칸에 입력'
        , default='1일'
    )
    payment_info = models.CharField(
        max_length=100,
        help_text='예: "10000원" 또는 "2시간" - 사용자가 한 칸에 입력', default='시급 10000원'
    )
    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        help_text='봉사시간 또는 지역화폐 선택'
    )
    description = models.TextField(max_length=300)  # 공백 포함 300자
    image_from_gallery = models.ImageField(
        upload_to='job_images/gallery/', blank=True, null=True
    )
    image_from_ai = models.ImageField(
        upload_to='job_images/ai/', blank=True, null=True
    )
    store_lat = models.FloatField()  # GPS 기반으로 자동 입력
    store_lng = models.FloatField()  # GPS 기반으로 자동 입력
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    liked_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_posts',
        blank=True
    )
    @property
    def like_count(self):
        return self.liked_users.count()

    def display_image(self):
        return self.image_from_gallery or self.image_from_ai

    def __str__(self):
        return f"{self.owner.store_name} - {self.duration_time} ({self.payment_type})"

class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', '대기'),
        ('accepted', '수락'),
        ('rejected', '거절'),
        ('matched', '매칭완료'),
        ('completed', '작업완료'),
    ]

    job_post = models.ForeignKey(
        JobPost,
        on_delete=models.CASCADE,
        related_name='applications' 
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    # 지원동기
    motivation = models.CharField(max_length=200, blank=True, null=True)
    # 재능 나누기 요청 상태
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.applicant} -> {self.job_post}"
