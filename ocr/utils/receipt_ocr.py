import pytesseract
from PIL import Image
import cv2
import numpy as np
import re
from wallet.models import Wallet, CoinHistory
from accounts.models import Profile, User

# 소상공인 프로필에서 리스트 가져오기
db_stores = list(Profile.objects.filter(role='owner').values('company_name', 'location'))


# OCR 전처리
def preprocess_receipt(image_path):
    data = np.fromfile(image_path, dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    
    #이미지 확대
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    
    #그레이스케일 + 블러
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3,3), 0)
    
    #명암이 다른 영수증 대응
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)
    
    #노이즈 제거
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    clean = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    
    return clean

# OCR 텍스트 추출
def extract_receipt_text(image):
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(image, lang='kor+eng', config=custom_config)
    return text

# 정보 추출
def parse_receipt(text):
    text = text.replace('\n', ' ').replace('\r', ' ')  # 줄바꿈 제거

    # 1. 업체명 
    store_match = re.search(r"(업체명|상호|가게|상호명)?\s*[:：]?\s*([^\d:：]+)", text)
    store_name = store_match.group(2).strip() if store_match else None

    # 2. 금액 
    
    amount_match = re.search(r"(총액|금액|합계)?\s*[:：]?\s*([\d,]+)원?", text)
    if amount_match:
        amount = int(amount_match.group(2).replace(',', ''))
    else:
        nums = re.findall(r'\d{3,}', text)
        amount = int(nums[-1]) if nums else None

    # 3. 지역
    region_match = re.search(r"(지역|주소)?\s*[:：]?\s*([가-힣\s]+)", text)
    if region_match:
        region = region_match.group(2).strip()
        region = ' '.join(region.split()[:2])
    else:
        region = None

    return store_name, amount, region

# DB 검증 후 코인 적립 가능 여부
def check_and_award(store_name, region, db_store_list):
    """
    db_store_list: [{'company_name': 'ABC 베이커리', 'location': '서울 강남구'}]
    """
    if not store_name or not region:
        return False

    store_name_normalized = store_name.replace(" ", "").lower()
    region_normalized = region.replace(" ", "").lower()

    for store in db_store_list:
        company_name_db = store.get('company_name', '').replace(" ", "").lower()
        location_db = store.get('location', '').replace(" ", "").lower()

        if store_name_normalized == company_name_db and region_normalized == location_db:
            return True

    return False
