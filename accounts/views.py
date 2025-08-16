from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Profile
from .serializers import UserSerializer, SignupSerializer, LoginSerializer, BusinessCertUploadSerializer
from ocr.utils.certificate_ocr import extract_business_info
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

# Create your views here.

# 회원가입
class SignupView(CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # User 객체 반환됨

        # 전체 User + Profile 반환
        output_serializer = UserSerializer(user)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

# 로그인
class LoginView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # 입력 값 검증, 직렬화
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # 토큰 발급
        refresh = RefreshToken.for_user(user)

        refresh['role'] = user.profile.role
        refresh['user_id'] = user.id
        refresh['email'] = user.email

        access = refresh.access_token
        access['role'] = user.profile.role
        access['user_id'] = user.id
        access['email'] = user.email

        return Response({
            'refresh': str(refresh),
            'access': str(access),
        })

# 소상공인 확인서 ocr 
class BusinessCertUploadView(APIView):
    def post(self, request):
        serializer = BusinessCertUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        business_cert = serializer.validated_data["business_cert"]

        # 파일을 임시로 저장
        path = default_storage.save(f"temp/{business_cert.name}", ContentFile(business_cert.read()))

        # OCR 정보 추출
        company_name, business_number, store_name, business_type = extract_business_info(default_storage.path(path))
        
        # 임시 파일 삭제 (선택)
        default_storage.delete(path)

        return Response({
            "대표자명": store_name,
            "사업자등록번호": business_number,
            "업체이름": company_name,
            "업종": business_type
        })