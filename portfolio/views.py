from django.shortcuts import render, get_object_or_404
from rest_framework import serializers
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from portfolio.models import Portfolio, TalentImage
from portfolio.serializers import PortfolioSerializer, TalentImageSerializer, PortfolioBasicUpdateSerializer, PortfolioIntroduceUpdateSerializer, ActivityUpdateSerializer

# Create your views here.

# 포트폴리오 조회
class PortfolioRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PortfolioSerializer

    def get_object(self):
        portfolio, created = Portfolio.objects.get_or_create(user=self.request.user)
        return portfolio

# 기본 정보 수정
class PortfolioBasicUpdateAPIView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PortfolioBasicUpdateSerializer

    def get_object(self):
        portfolio, _ = Portfolio.objects.get_or_create(user=self.request.user)
        return portfolio

# 자기소개 수정
class PortfolioIntroduceUpdateAPIView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PortfolioIntroduceUpdateSerializer

    def get_object(self):
        portfolio, created = Portfolio.objects.get_or_create(user=self.request.user)
        return portfolio

    def update(self, request, *args, **kwargs):
        portfolio = self.get_object()
        serializer = self.get_serializer(portfolio, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_portfolio = serializer.save()
        return Response(PortfolioSerializer(updated_portfolio).data, status=status.HTTP_200_OK)

# AI 포트폴리오 수정
class ActivityUpdateAPIView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ActivityUpdateSerializer
    lookup_url_kwarg = 'activity_id'

    def get_queryset(self):
        return Activities.objects.filter(portfolio__user=self.request.user)

# 이미지 업로드
class TalentImageCreateAPIView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TalentImageSerializer
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        portfolio, _ = Portfolio.objects.get_or_create(user=self.request.user)
        if portfolio.images.count() >= 9:
            raise serializers.ValidationError("최대 9개의 이미지만 첨부 가능합니다.")
        serializer.save(portfolio=portfolio)

# 이미지 삭제
class TalentImageDeleteAPIView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        image_id = self.kwargs['image_id']
        return get_object_or_404(TalentImage, id=image_id, portfolio__user=self.request.user)