from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Partner, RedeemCode
from .serializers import WalletSerializer, RedeemCodeSerializer, CoinHistorySerializer
from .services import process_receipt, process_ad, redeem_coin


class WalletView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(WalletSerializer(request.user.wallet).data)


class ReceiptView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        partner_id = request.data.get("partner_id")
        amount = int(request.data.get("amount"))
        try:
            partner = Partner.objects.get(id=partner_id)
        except Partner.DoesNotExist:
            return Response({"error": "등록되지 않은 업체"}, status=400)

        earned, stamp = process_receipt(request.user, partner, amount)
        return Response({"earned": earned, "stamp_progress": f"{stamp}/10"})


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
