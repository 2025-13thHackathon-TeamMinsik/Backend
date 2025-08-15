from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Profile

class SignupSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=Profile.ROLE_CHOICES) # 역할
    skill_1 = serializers.ChoiceField(choices=Profile.SKILL_CHOICES)
    skill_2 = serializers.ChoiceField(choices=Profile.SKILL_CHOICES)

    class Meta:
        model = User
        fields = ['email', 'password', 'birth', 'phone', 'role', 'skill_1', 'skill_2']
        extra_kwargs = {
            'password' : {'write_only':True}
        }

    # 역할별 필드 입력
    # 1. 대학생
    university = serializers.CharField(required=False, allow_blank=True)
    major = serializers.CharField(required=False, allow_blank=True)
    double_major = serializers.CharField(required=False, allow_blank=True)
    academic_status = serializers.CharField(required=False, allow_blank=True)
    
    # 2. 소상공인
    store_name = serializers.CharField(required=False, allow_blank=True)
    business_number = serializers.CharField(required=False, allow_blank=True)
    business_cert = serializers.FileField(required=False)

    def validate(self, attrs):
        if attrs['skill_1'] == attrs['skill_2']:
            raise serializers.ValidationError("skill_1과 skill_2는 서로 달라야 합니다.")
        return attrs
    
    def create(self, validated_data):
        role = validated_data.pop('role')

        # 유저 생성
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        # profile 생성
        if role == 'student':
            profile_data.update({
                'university': self.validated_data.get('university'),
                'major': self.validated_data.get('major'),
                'double_major': self.validated_data.get('double_major'),
                'academic_status': self.validated_data.get('academic_status'),
            })
        elif role == 'owner':
            profile_data.update({
                'store_name': self.validated_data.get('store_name'),
                'business_number': self.validated_data.get('business_number'),
                'business_cert': self.validated_data.get('business_cert'),
            })
        Profile.objects.create(user=user, **profile_data)
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("이메일 또는 비밀번호가 올바르지 않습니다.")
        data['user'] = user
        return data