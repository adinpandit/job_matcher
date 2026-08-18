from app.resume.resume_parsers.pdf_parser import get_resume_text
from app.resume.resume_parsers.resume_parser import parse_resume
from app.resume.resume_skills.skill_extractor import extract_skill
from app.resume.resume_skills.skill_normalizer import normalize_skills

def main():

    cleaned_text = get_resume_text()

    if not cleaned_text:
        print("could not extract resume text.")
        return

    parsed_resume = parse_resume(cleaned_text)

    resume_skills = extract_skill(parsed_resume)

    normalized_skills = normalize_skills(resume_skills)

    print(normalized_skills)

if __name__ == "__main__":
    main()