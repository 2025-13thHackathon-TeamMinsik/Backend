import pytesseract
from PIL import Image

def extract_business_info(image_path):
    text = pytesseract.image_to_string(Image.open(image_path), lang='kor+eng')

    company_name = None
    business_number = None
    store_name = None
    business_type = None

    for line in text.split("\n"):
        line = line.strip()
        if "기업명" in line:
            company_name = line.split()[-1]
        elif "사업자등록번호" in line:
            business_number = line.split()[-1]
        elif "대표자명" in line:
            store_name = line.split()[-1]
        elif "업종" in line:
            business_type = line.split()[-1]

    return company_name, business_number, store_name, business_type
        