from pathlib import Path

from app.text_extractor.pdf_extractor import extract_pdf
from app.text_extractor.text_cleaner import clean_text
from app.text_extractor.img_extractor import extract_image

def get_resume_text()->str:
    project_root = Path(__file__).resolve().parent.parent.parent
    resume_path = project_root / "samples" / "resume.pdf"

    try:

        raw_text = extract_pdf(resume_path)
        cleaned_text = clean_text(raw_text)
        
        if not cleaned_text:
            resume_path = project_root / "samples" / "resume.jpg"
            raw_text = extract_image(resume_path)
            cleaned_text = clean_text(raw_text)

        if not cleaned_text:
            print("No text could be extracted from the resume.")
            return ""

        return cleaned_text

    except FileNotFoundError as error:
        print(error)

    except ValueError as error:
        print(error)

    except Exception as error:
        print(f"Unexpected error: {error}")

    return ""