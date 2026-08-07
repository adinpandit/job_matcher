from pathlib import Path
import pytesseract
from pdf2image import convert_from_path

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

def extract_pdf(file_path:str|Path)->str:
    path = Path(file_path)

    if not path.exists():
        return FileNotFoundError(f"PDF not found: {path}")

    images = convert_from_path(path)

    extracted_pages:list[str]=[]

    for image in images:
        page_text = pytesseract.image_to_string(image)

        if page_text.strip():
            extracted_pages.append(page_text)
    return "\n".join(extracted_pages).strip()   

    