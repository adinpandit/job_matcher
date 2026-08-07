from pathlib import Path

import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

def extract_image(file_path: str|Path)->str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    image = Image.open(path)

    extracted_text = pytesseract.image_to_string(image)

    return extracted_text.strip()