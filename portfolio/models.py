from django.db import models
from django.conf import settings
from jobs.models import JobPost, Application
from .services.ai_portfolio import generate_ai_portfolio
User = settings.AUTH_USER_MODEL

# Create your models here.

def profile_upload_path(instance, filename):
    # portfolio/profile_img/user_<id>/<filename>
    return f"portfolio/profile_img/user_{instance.user.id}/{filename}"

def talent_upload_path(instance, filename):
    # portfolio/talent_img/portfolio_<id>/<filename>
    return f"portfolio/talent_img/portfolio_{instance.portfolio.id}/{filename}"

class Portfolio(models.Model):
    # 유저 정보
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="portfolio")
    # 프로필
    profile_img = models.ImageField(upload_to=profile_upload_path, blank=True, null=True)
    # 자기소개
    self_introduce = models.CharField(max_length=200, blank=True, null=True) 
    # 재능 관람-url
    talent_url = models.URLField(blank=True, null=True)
    # 추천 노출 여부
    show_for_recommendation = models.BooleanField(default=True)

# 활동 이력
class Activities(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="activities")
    # 업체명, 활동 기간 필요
    job = models.ForeignKey("jobs.JobPost", on_delete=models.CASCADE, related_name="activities")
    # 지원 동기 필요
    application = models.OneToOneField("jobs.Application", on_delete=models.CASCADE, related_name="activity")    
    # ai 포트폴리오
    ai_portfolio_summary = models.CharField(max_length=120, blank=True, null=True)

# 이미지들
class TalentImage(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=talent_upload_path, blank=True, null=True)