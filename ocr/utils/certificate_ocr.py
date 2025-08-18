import re
import cv2
import pytesseract
from PIL import Image
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_business_info(image_path):
    # 이미지 경로 미리보기 
    # print('이미지 경로' + image_path)

    # 한글 경로 decode
    data = np.fromfile(image_path, dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_UNCHANGED)
    
    # 이미지 사이즈 키우기
    img = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    
    # 전처리
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Morphology로 노이즈 제거
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    clean = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

    # OCR (최적 옵션 적용)
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(thresh, lang='kor', config=custom_config)

    # ocr 결과 이미지 미리보기 
    # cv2.imshow("thresh", thresh)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # ocr 결과 텍스트 확인 
    # print('ocr 결과:\n' + text)

    company_match = re.search(r"기\s*업\s*명\s*[:：]?\s*(.+)", text)
    company_name = company_match.group(1).strip() if company_match else None

    business_number_match = re.search(r"사업자등록번호\s*[:：]?\s*([\d-]+)", text)
    business_number = business_number_match.group(1).strip() if business_number_match else None

    ceo_name_match = re.search(r"대표자명\s*[:：]?\s*(.+)", text)
    ceo_name = ceo_name_match.group(1).strip() if ceo_name_match else None

    business_type_match = re.search(r"업종[:\s]*([^\n]+)", text)
    business_type = business_type_match.group(1).strip() if business_type_match else None

    print('company_name:' , company_name)
    print('business_number:' , business_number)
    print('ceo_name:' , ceo_name)
    # print('business_type:' + business_type)    

    return company_name, business_number, ceo_name, business_type
        