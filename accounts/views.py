from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Profile
from .serializers import UserSerializer, SignupSerializer, LoginSerializer
from ocr.utils.certificate_ocr import extract_business_info

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
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

# 소상공인 확인서 ocr 
class BusinessCertUploadView(APIView):
    def post(self, request):
        user = request.user
        user.business_cert = request.FILES['business_cert']
        user.save()

        # ocr에서 가져옴
        company_name, business_number, store_name, business_type = extract_business_info(user.business_cert.path)

        user.store_name = store_name
        user.business_number = business_number
        user.company_name = company_name
        user.business_type = business_type
        user.save()

        return Response({
            "대표자명": store_name,
            "사업자등록번호": business_number,
            "업체이름": company_name,
            "업종": business_type
        })