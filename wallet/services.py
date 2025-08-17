from .models import Wallet, Receipt, CoinHistory
#OCR 인증 후 적립 처리
def process_receipt(user, partner, amount):
    wallet, _ = Wallet.objects.get_or_create(user=user)

    # 5% 코인 적립
    earned = amount * 5 // 100
    wallet.coin_balance += earned
    wallet.stamp_count += 1

    # 최근 10개 기록 관리
    history = wallet.last_ten_coins
    history.append(earned)
    if len(history) > 10:
        history = history[-10:]
    wallet.last_ten_coins = history

    wallet.save()

    Receipt.objects.create(user=user, partner=partner, amount=amount)
    CoinHistory.objects.create(user=user, amount=earned, description="영수증 적립")

    return earned, wallet.stamp_count

#광고 시청 완료 처리
def process_ad(user):
    wallet = user.wallet
    if wallet.stamp_count < 10 or wallet.ad_watched:
        return None

    avg = sum(wallet.last_ten_coins) // len(wallet.last_ten_coins)
    wallet.coin_balance += avg
    CoinHistory.objects.create(user=user, amount=avg, description="광고 보상")

    # 리셋
    wallet.stamp_count = 0
    wallet.last_ten_coins = []
    wallet.ad_watched = True
    wallet.save()

    return avg

from .models import RedeemCode

#발급 기능
def redeem_coin(user, amount):
    wallet = user.wallet
    if wallet.coin_balance < amount:
        raise ValueError("잔액 부족")

    wallet.coin_balance -= amount
    wallet.save()

    code = RedeemCode.generate_code()
    redeem = RedeemCode.objects.create(user=user, code=code, amount=amount)
    CoinHistory.objects.create(user=user, amount=-amount, description="코인 발급")

    return redeem