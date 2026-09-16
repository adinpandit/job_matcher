from pathlib import Path

import fitz
import pytesseract

from pdf2image import convert_from_path
from PIL import ImageOps


# ============================================================
# CONFIGURATION
# ============================================================

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def preprocess_image(image):
    """
    Prepare an image for OCR.

    Steps:
        1. Convert to grayscale
        2. Increase contrast
        3. Resize for better OCR accuracy
    """

    image = ImageOps.grayscale(image)

    image = ImageOps.autocontrast(image)

    image = image.resize(
        (
            image.width * 2,
            image.height * 2,
        )
    )

    return image


# ============================================================
# NATIVE PDF EXTRACTION
# ============================================================

def extract_pdf_native(file_path: Path) -> str:
    """
    Extract text directly from the PDF text layer.

    This is preferred over OCR because native PDF text
    generally preserves text more accurately.
    """

    doc = fitz.open(file_path)

    pages = []

    for page in doc:

        text = page.get_text(
            "text",
            sort=True,
        )

        if text.strip():
            pages.append(text)

    doc.close()

    return "\n".join(pages).strip()


# ============================================================
# OCR PDF EXTRACTION
# ============================================================

def extract_pdf_ocr(file_path: Path) -> str:
    """
    Convert PDF pages to images and extract text using OCR.
    """

    images = convert_from_path(
        file_path,
        dpi=300,
    )

    pages = []

    for image in images:

        image = preprocess_image(image)

        text = pytesseract.image_to_string(
            image,
            config="--oem 3 --psm 6",
        )

        if text.strip():
            pages.append(text)

    return "\n".join(pages).strip()


# ============================================================
# MAIN PDF EXTRACTOR
# ============================================================

def extract_pdf(file_path: str | Path) -> str:
    """
    Extract text from a PDF.

    Strategy:

        PDF
         ↓
        Native extraction
         ↓
        If insufficient text
         ↓
        OCR fallback
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"PDF not found: {path}"
        )

    if path.suffix.lower() != ".pdf":
        raise ValueError(
            f"Expected a PDF file, got: {path.suffix}"
        )

    # --------------------------------------------------------
    # Try native extraction first
    # --------------------------------------------------------

    native_text = extract_pdf_native(path)

    if len(native_text.strip()) >= 100:
        return native_text.strip()

    # --------------------------------------------------------
    # OCR fallback
    # --------------------------------------------------------

    ocr_text = extract_pdf_ocr(path)

    return ocr_text.strip()