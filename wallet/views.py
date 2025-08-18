from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import CoinHistory, Partner, RedeemCode
from .serializers import WalletSerializer, RedeemCodeSerializer, CoinHistorySerializer
from .services import process_receipt, process_ad, redeem_coin
from wallet.models import Wallet
import os
from ocr.utils.receipt_ocr import preprocess_receipt, extract_receipt_text, parse_receipt, check_and_award
from accounts.models import Profile

class WalletView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        return Response(WalletSerializer(wallet).data)

class ReceiptView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 업로드 파일 확인
        uploaded_file = request.FILES.get('receipt')
        if not uploaded_file:
            return Response({"error": "파일이 업로드되지 않았습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 임시 경로 저장
        tmp_dir = 'tmp_receipts'
        os.makedirs(tmp_dir, exist_ok=True)
        tmp_path = os.path.join(tmp_dir, uploaded_file.name)
        with open(tmp_path, 'wb+') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        # OCR 처리
        try:
            img = preprocess_receipt(tmp_path)
            text = extract_receipt_text(img)
            store_name, amount, region = parse_receipt(text)
        except Exception as e:
            return Response({"error": f"OCR 처리 실패: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not store_name or not region or not amount:
            return Response({"error": "영수증에서 필요한 정보를 추출하지 못했습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # DB 매칭: accounts.Profile에서 소상공인 목록 조회
        db_stores = list(Profile.objects.filter(role='owner').values('company_name', 'location'))
        coin_awarded = check_and_award(store_name, region, db_stores)

        if not coin_awarded:
            return Response({"error": "업체명 또는 지역 불일치"}, status=status.HTTP_400_BAD_REQUEST)

        # 코인 적립
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        earned = amount * 5 // 100
        wallet.coin_balance += earned
        wallet.stamp_count += 1

        # 최근 10개 기록 관리
        history = wallet.last_ten_coins or []
        history.append(earned)
        if len(history) > 10:
            history = history[-10:]
        wallet.last_ten_coins = history
        wallet.save()

        # 기록 남기기
        CoinHistory.objects.create(user=request.user, amount=earned, description="영수증 적립")

        return Response({
            "company_name": store_name,
            "amount": amount,
            "region": region,
            "earned": earned,
            "stamp_progress": f"{wallet.stamp_count}/10",
            "wallet_balance": wallet.coin_balance
        })

class AdRewardView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        reward = process_ad(request.user)
        if reward is None:
            return Response({"message": "광고 보상 불가"}, status=400)
        return Response({"reward": reward})


class RedeemView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = int(request.data.get("amount"))
        try:
            redeem = redeem_coin(request.user, amount)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        return Response(RedeemCodeSerializer(redeem).data)


class RedeemHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        codes = RedeemCode.objects.filter(user=request.user).order_by("-created_at")
        return Response(RedeemCodeSerializer(codes, many=True).data)
