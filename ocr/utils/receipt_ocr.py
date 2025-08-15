import pytesseract
from PIL import Image

def extract_recipt_info(image_path):
    text = pytesseract.image_to_string(Image.open(image_path), lang='kor+eng')

    