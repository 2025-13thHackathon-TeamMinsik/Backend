from rest_framework import serializers
from .models import Portfolio, Activities, TalentImage
from accounts.serializers import UserSerializer
from accounts.models import Profile, User

# 재능 관람-이미지
class TalentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TalentImage
        fields = ['id', 'image']

# 활동 이력
class ActivitiesSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='job.owner.profile.company_name', read_only=True)
    duration_time = serializers.CharField(source='job.duration_time', read_only=True)
    skills = serializers.SerializerMethodField()

    class Meta:
        model = Activities
        fields = [
            'id', 'company_name', 'skills', 'duration_time', 'ai_portfolio_summary'
        ]

    def get_skills(self, obj):
        profile = obj.application.applicant.profile  # 지원자 Profile에서 skill 가져오기
        return [profile.skill_1, profile.skill_2]

# 포트폴리오 조회
class PortfolioSerializer(serializers.ModelSerializer):
    user_info = UserSerializer(source='user', read_only=True)
    activities = ActivitiesSerializer(many=True, read_only=True)
    images = TalentImageSerializer(many=True, read_only=True)

    class Meta:
        model = Portfolio
        fields = [
            'user_info', 'self_introduce', 'activities',
            'talent_url', 'images', 
            'show_for_recommendation',  # 소상공인 추천 노출 여부
        ]

    def validate_images(self, value): # 이미지 최대 9개
        if len(value) > 9:
            raise serializers.ValidationError("이미지는 최대 9개까지 첨부 가능합니다.")
        return value

# 기본정보 수정
class PortfolioBasicUpdateSerializer(serializers.ModelSerializer):
    # User 정보
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    full_name = serializers.CharField(source='user.full_name', required=False)
    birth = serializers.DateField(source='user.birth', required=False)
    gender = serializers.CharField(source='user.gender', required=False)
    phone = serializers.CharField(source='user.phone', required=False)
    email = serializers.EmailField(source='user.email', required=False)
    password = serializers.CharField(source='user.password', required=False)

    # Profile 정보 (대학생)
    university = serializers.CharField(source='user.profile.university', required=False)
    major = serializers.CharField(source='user.profile.major', required=False)
    academic_status = serializers.CharField(source='user.profile.academic_status', required=False)
    skill_1 = serializers.CharField(source='user.profile.skill_1', required=False)
    skill_2 = serializers.CharField(source='user.profile.skill_2', required=False)
    location = serializers.CharField(source='user.profile.location', required=False)

    # Portfolio 정보
    show_for_recommendation = serializers.BooleanField(required=False)

    class Meta:
        model = Portfolio
        fields = [
            'user_id',
            'profile_img', 'full_name', 'birth', 'gender', 'phone', 'email', 'password', 'location',
            'university', 'major', 'academic_status',
            'skill_1', 'skill_2', 'show_for_recommendation' 
        ]
    
    def update(self, instance, validated_data):
        new_password = None
        print(validated_data)
        # 프로필 사진 업데이트
        profile_img = validated_data.pop('profile_img', None)
        if profile_img:
            instance.profile_img = profile_img

        # User 필드 업데이트
        user_data = validated_data.pop('user', {})
        if 'password' in user_data:
            new_password = user_data.pop('password')
            instance.user.set_password(new_password)

        for attr, value in user_data.items():
            if attr != "profile":
                setattr(instance.user, attr, value)
        instance.user.save()

        # Profile 필드 업데이트
        profile_data = user_data.get('profile', {})
        for attr, value in profile_data.items():
            setattr(instance.user.profile, attr, value)
        if profile_data:
            instance.user.profile.save()

        # Portfolio 필드 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 평문 password 임시저장
        instance._plain_password = new_password
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if hasattr(instance, "_plain_password") and instance._plain_password:
            data["password"] = instance._plain_password  # 해시 대신 평문 반환
        return data

# 자기소개 수정
class PortfolioIntroduceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ['self_introduce']

# AI 포트폴리오 수정
class ActivityUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activities
        fields = ['ai_portfolio_summary']
