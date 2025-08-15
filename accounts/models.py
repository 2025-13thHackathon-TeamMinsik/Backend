from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

# 공통 인증 관련 데이터
class User(AbstractUser): 
	name = models.CharField(max_length=50)
	birth = models.DateField(null=True, blank=True)
	phone = models.CharField(max_length=20)
	email = models.EmailField(unique=True)
	password = models.CharField(max_length=12)
	
#사용자 유형별 프로필 정보
class Profile(models.Model):
	ROLE_CHOICES = (
        ('student', '대학생'),
        ('owner', '소상공인'),
    )

	SKILL_CHOICES = (
        ('design', '디자인'),
        ('photo_video', '영상/사진'),
        ('craft', '공예'),
        ('coding', '코딩/개발'),
        ('language', '외국어/번역'),
        ('marketing', '홍보/마케팅'),
        ('document', '문서 작성'),
        ('counsel', '상담'),
        ('volunteer', '자원봉사'),
    )

	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
	role = models.CharField(max_length=20, choices=ROLE_CHOICES)
	
	#공통 프로필
	skill_1 = models.CharField(max_length=20, choices=SKILL_CHOICES)
	skill_2 = models.CharField(max_length=20, choices=SKILL_CHOICES)
	
	#대학생 전용
	university = models.CharField(max_length=100, blank=True, null=True) #대학교
	major = models.CharField(max_length=100, blank=True, null=True) # 본 전공
	double_major = models.CharField(max_length=100, blank=True, null=True) # 복수전공
	academic_status = models.CharField(max_length=20, blank=True, null=True) # 학년
	 
	#소상공인 전용
	store_name = models.CharField(max_length=100, blank=True, null=True)
	business_number = models.CharField(max_length=30, blank=True, null=True)
	business_cert = models.FileField(upload_to="certs/", blank=True, null=True) #pdf or jpg