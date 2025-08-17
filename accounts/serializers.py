from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Profile

class UserSerializer(serializers.ModelSerializer):
    # Profile 필드 읽기 전용으로 가져오기
    role = serializers.CharField(source='profile.role', read_only=True)
    full_name = serializers.CharField(write_only=True, required=True)
    skill_1 = serializers.CharField(source='profile.skill_1', read_only=True)
    skill_2 = serializers.CharField(source='profile.skill_2', read_only=True)
    location = serializers.CharField(source='profile.location', read_only=True)

    # 대학생 전용
    university = serializers.CharField(source='profile.university', read_only=True)
    major = serializers.CharField(source='profile.major', read_only=True)
    double_major = serializers.CharField(source='profile.double_major', read_only=True)
    academic_status = serializers.CharField(source='profile.academic_status', read_only=True)

    # 소상공인 전용
    ceo_name = serializers.CharField(source='profile.ceo_name', read_only=True)
    business_number = serializers.CharField(source='profile.business_number', read_only=True)
    company_name = serializers.CharField(source='profile.company_name', read_only=True)
    business_type = serializers.CharField(source='profile.business_type', read_only=True)
    business_cert = serializers.ImageField(source='profile.business_cert', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', "full_name", 'birth', 'phone',
            'role', 'skill_1', 'skill_2', 'location',
            'university', 'major', 'double_major', 'academic_status',
            'ceo_name', 'business_number', 'company_name', 'business_type', 'business_cert',
        ]

class SignupSerializer(serializers.ModelSerializer):
    # 공통 필드
    role = serializers.ChoiceField(choices=Profile.ROLE_CHOICES, write_only=True) # 역할
    full_name = serializers.CharField(write_only=True, required=True)
    skill_1 = serializers.ChoiceField(choices=Profile.SKILL_CHOICES, write_only=True)
    skill_2 = serializers.ChoiceField(choices=Profile.SKILL_CHOICES, write_only=True)
    password = serializers.CharField(write_only=True)
    location = serializers.CharField(required=False, allow_blank=True, write_only=True)

    # 대학생 필드
    university = serializers.CharField(required=False, allow_blank=True)
    major = serializers.CharField(required=False, allow_blank=True)
    double_major = serializers.CharField(required=False, allow_blank=True)
    academic_status = serializers.CharField(required=False, allow_blank=True)
    
    # 소상공인 필드
    ceo_name = serializers.CharField(required=False, allow_blank=True)
    business_number = serializers.CharField(required=False, allow_blank=True)
    company_name = serializers.CharField(required=False, allow_blank=True)
    business_type = serializers.CharField(required=False, allow_blank=True)
    business_cert = serializers.FileField(required=False)

    class Meta:
        model = User
        fields = [
            'email', 'password', "full_name",'birth', 'phone', 'role', 'location',
            'skill_1', 'skill_2',  'full_name', 
            'university', 'major', 'double_major', 'academic_status',
            'ceo_name', 'business_number', 'company_name', 'business_type', 'business_cert',
        ]
        extra_kwargs = {
            'password' : {'write_only':True}
        }

    def validate(self, attrs):
        if attrs['skill_1'] == attrs['skill_2']:
            raise serializers.ValidationError("skill_1과 skill_2는 서로 달라야 합니다.")
        return attrs
    
    def create(self, validated_data):
        role = validated_data['role']
        full_name = validated_data.pop('full_name')
        password = validated_data.pop('password')

        # User 생성
        user = User.objects.create(
            full_name=full_name,
            email=validated_data['email'], 
            phone=validated_data.get('phone'),
            birth=validated_data.get('birth')
        )
        user.set_password(password)
        user.save()

        # Profile  생성
        profile_data = {
            "user": user,
            'role': validated_data.pop('role', None),
            'skill_1': validated_data.pop('skill_1', None),
            'skill_2': validated_data.pop('skill_2', None),
            'location': validated_data.pop('location', None),
            'university': validated_data.pop('university', None),
            'major': validated_data.pop('major', None),
            'double_major': validated_data.pop('double_major', None),
            'academic_status': validated_data.pop('academic_status', None),
            'ceo_name': validated_data.pop('ceo_name', None),
            'business_number': validated_data.pop('business_number', None),
            'company_name': validated_data.pop('company_name', None),
            'business_type': validated_data.pop('business_type', None),
            'business_cert': validated_data.pop('business_cert', None),
        }
        Profile.objects.create(**profile_data)

        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        print("DEBUG email:", data["email"])
        print("DEBUG password:", data["password"])
        user = authenticate(
            request=self.context.get('request'),
            email=data['email'],
            password=data['password'],
        )
        if not user:
            raise serializers.ValidationError("이메일 또는 비밀번호가 올바르지 않습니다.")
        data['user'] = user
        return data

class BusinessCertUploadSerializer(serializers.Serializer):
    business_cert = serializers.ImageField()
    ceo_name = serializers.CharField(required=False, allow_blank=True)
    business_number = serializers.CharField(required=False, allow_blank=True)
    company_name = serializers.CharField(required=False, allow_blank=True)
    business_type = serializers.CharField(required=False, allow_blank=True)
    business_cert = serializers.FileField(required=False)

    class Meta:
        model: Profile
        fields = [
            'ceo_name', 'business_number', 'company_name', 'business_type', 'business_cert',
        ]
