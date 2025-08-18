from rest_framework import serializers
from .models import Wallet, CoinHistory, RedeemCode, Receipt


class WalletSerializer(serializers.ModelSerializer):
    progress = serializers.SerializerMethodField()
    class Meta:
        model = Wallet
        fields = ["coin_balance", "stamp_count", "progress",'last_ten_coins']
    def get_progress(self, obj):
        return f"{obj.stamp_count}/10"


class CoinHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinHistory
        fields = ["amount", "description", "created_at"]


class RedeemCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RedeemCode
        fields = ["code", "amount", "created_at"]


class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = ["partner", "amount", "created_at"]
