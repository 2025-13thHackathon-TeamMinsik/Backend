import pytesseract
from PIL import Image
import cv2
import numpy as np
import re
from wallet.models import Wallet, CoinHistory
from accounts.models import Profile, User

# 소상공인 프로필에서 리스트 가져오기
try:
    db_stores = list(Profile.objects.filter(role='owner').values('company_name', 'location'))
except:
    db_stores = []


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
    text = text.replace('\n', ' ').replace('\r', ' ')
    text = re.sub(r'\s+', '', text) 

    # 업체명
    store_match = re.search(r"(상호명|업체명|상호)\s*[:：]?\s*([가-힣A-Za-z0-9]+)", text)
    store_name = store_match.group(2) if store_match else None
    if store_name:
        store_name = re.sub(r'등록번호.*', '', store_name)

    # 금액
    amount = None
    amount_matches = re.findall(r'(?:합계금액|총액|금액)[^0-9]*([\d,]+)', text)
    if amount_matches:
        amount = int(amount_matches[-1].replace(',', ''))
    else:
        nums = re.findall(r'\d{3,}', text)
        if nums:
            amount = int(nums[-1].replace(',', ''))

    # 지역
    region_match = re.search(r"(주소)[^가-힣]*([가-힣]+)", text)
    region = region_match.group(2) if region_match else None

    # 시/구 단위만 추출
    if region:
        parts = re.findall(r'[가-힣]+[시구]', region)
        if parts:
            region = parts[-1]

    return store_name, amount, region


# DB 검증 후 코인 적립 가능 여부
def check_and_award(store_name, region, db_store_list):
    if not store_name or not region:
        return False

    store_name_normalized = store_name.replace(" ", "").strip().lower()
    region_normalized = region.replace(" ", "").strip().lower()

    for store in db_store_list:
        company_name_db = store.get('company_name', '').replace(" ", "").strip().lower()
        location_db = store.get('location', '').replace(" ", "").strip().lower()

        if (store_name_normalized in company_name_db or company_name_db in store_name_normalized) and \
           (region_normalized in location_db or location_db in region_normalized):
            return True

    return False