import re
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_business_info(image_path):
    print('이미지 경로' + image_path)
    text = pytesseract.image_to_string(Image.open(image_path), lang='kor+eng')

    company_name = re.search(r"기업명[:\s]*([^\n]+)", text)
    business_number = re.search(r"사업자등록번호[:\s]*([\d\-]+)", text)
    store_name = re.search(r"대표자명[:\s]*([^\n]+)", text)
    business_type = re.search(r"업종[:\s]*([^\n]+)", text)

    return (
        company_name.group(1).strip() if company_name else None,
        business_number.group(1).strip() if business_number else None,
        store_name.group(1).strip() if store_name else None,
        business_type.group(1).strip() if business_type else None
    )
        