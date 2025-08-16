from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("이메일은 필수 입력 항목입니다.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # 비밀번호 해싱
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser는 is_staff=True 이어야 합니다.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser는 is_superuser=True 이어야 합니다.")

        return self.create_user(email, password, **extra_fields)

# 공통 인증 관련 데이터
class User(AbstractBaseUser, PermissionsMixin): 
	email = models.EmailField(unique=True)
	full_name = models.CharField(max_length=50)
	phone = models.CharField(max_length=20, blank=True, null=True)
	birth = models.DateField(blank=True, null=True)

	# Django 기본 필드 대체
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)
	
	objects = UserManager()
	
	USERNAME_FIELD = "email"      # 로그인 시 사용할 필드
	REQUIRED_FIELDS = []          # createsuperuser 시 추가 입력 받을 필드 (없음)
	
	def __str__(self):
		return self.email
		
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
	location = models.CharField(max_length=300, blank=True, null=True)
	
	#대학생 전용
	university = models.CharField(max_length=100, blank=True, null=True) #대학교
	major = models.CharField(max_length=100, blank=True, null=True) # 본 전공
	double_major = models.CharField(max_length=100, blank=True, null=True) # 복수전공
	academic_status = models.CharField(max_length=20, blank=True, null=True) # 학년
	 
	#소상공인 전용
	store_name = models.CharField(max_length=100, blank=True, null=True) # 대표자명
	business_number = models.CharField(max_length=30, blank=True, null=True) # 사업자번호
	company_name = models.CharField( max_length=200, blank=True, null=True) # 업체명
	business_type = models.CharField(max_length=100, blank=True, null=True) # 업종
	business_cert = models.ImageField(upload_to="certs/", blank=True, null=True) #확인서: jpg