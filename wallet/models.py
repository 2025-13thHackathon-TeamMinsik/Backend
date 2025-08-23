from django.db import models
import uuid, random, string
from django.conf import settings
from django.utils.timezone import now

User = settings.AUTH_USER_MODEL


class Partner(models.Model): #재능곳간에 등록된 업체인지
    name = models.CharField(max_length=100)
    business_number = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Wallet(models.Model): 
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet")
    coin_balance = models.PositiveIntegerField(default=0)  # 참새코인
    stamp_count = models.PositiveIntegerField(default=0)   # 현재 스탬프 진행
    ad_watched = models.BooleanField(default=False)        # 광고 봤는지 여부
    last_ten_coins = models.JSONField(default=list)        # 최근 10번 코인 적립 기록

    def __str__(self):
        return f"{self.user.full_name} wallet"


class Receipt(models.Model): #영수증기록
    user = models.ForeignKey(User, on_delete=models.CASCADE) #영수증 주인
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE) #재능곳간에 등록한 파트너 업체
    amount = models.PositiveIntegerField()  # 소비 금액
    created_at = models.DateTimeField(auto_now_add=True)


class CoinHistory(models.Model): #코인 적립, 사용 내역
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()  # + 적립, - 차감
    description = models.CharField(max_length=200) 
    created_at = models.DateTimeField(auto_now_add=True)


class RedeemCode(models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=30, unique=True)
    amount = models.PositiveIntegerField() 
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.code

    @staticmethod
    def generate_code(): #랜덤 코드 생성 RGC-XXXX-XXXX-XXXX 현식
        parts = []
        for _ in range(3):
            part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            parts.append(part)
        return "RGC-" + "-".join(parts)
