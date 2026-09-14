from app.resume.resume_parsers.pdf_parser import get_resume_text
from app.resume.resume_parsers.resume_parser import parse_resume
from app.resume.resume_skills.skill_extractor import extract_skill
from app.resume.resume_skills.skill_normalizer import normalize_skills
from app.Job_description.jd_parser import parse_jd
from app.Job_description.jd_skill_extractor import extract_jd_skills
from samples.jd import jd
from app.exact_matcher import exact_match
from app.semantic_matcher import semantic_match

def main():

    cleaned_text = get_resume_text()

    if not cleaned_text:
        print("could not extract resume text.")
        return

    parsed_resume = parse_resume(cleaned_text)

    resume_skills = extract_skill(parsed_resume)

    normalized_skills = normalize_skills(resume_skills)

    print(normalized_skills)

    print("\n")

    parsed_jd = parse_jd(jd)

    print(parsed_jd)

    print("\n")

    jd_skills = extract_jd_skills(parsed_jd["sections"])

    exact_matched_skills = exact_match(normalized_skills,jd_skills["required_skills"],jd_skills["preferred_skills"])

    print(exact_matched_skills)

    print("\n")

    matches = semantic_match(parsed_resume , parsed_jd)

    print(matches)

if __name__ == "__main__":
    main()