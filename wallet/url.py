from django.urls import path
from .views import (
    WalletView,
    ReceiptView,
    AdRewardView,
    RedeemView,
    RedeemHistoryView,
)

urlpatterns = [
    path("", WalletView.as_view(), name="wallet"),                                # 내 지갑 조회
    path("receipt/", ReceiptView.as_view(), name="receipt"),                     # 영수증 등록 (업체ID + 금액)
    path("ad-reward/", AdRewardView.as_view(), name="ad_reward"),               # 광고 시청 보상
    path("redeem/", RedeemView.as_view(), name="redeem"),                        # 코인 발급
    path("redeem/history/", RedeemHistoryView.as_view(), name="redeem_history"), # 발급 내역 조회
]
