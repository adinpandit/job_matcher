from app.resume.resume_parsers.pdf_parser import get_resume_text
from app.resume.resume_parsers.resume_parser import parse_resume

from app.Job_description.jd_parser import parse_jd

from samples.jd import jd


def main():

    # ========================================================
    # RESUME
    # ========================================================

    print("\n" + "=" * 60)
    print("RESUME")
    print("=" * 60)

    resume_text = get_resume_text()

    print("\nEXTRACTED RESUME TEXT\n")
    print(resume_text)

    parsed_resume = parse_resume(resume_text)

    print("\n" + "=" * 60)
    print("PARSED RESUME")
    print("=" * 60)

    print("\nName:")
    print(parsed_resume.get("name", ""))

    print("\nContact:")
    print(parsed_resume.get("contact", {}))

    print("\nSkills:")
    print(parsed_resume.get("skills", []))

    print("\nExperience:")
    for experience in parsed_resume.get("experience", []):
        print(experience)

    print("\nProjects:")
    for project in parsed_resume.get("projects", []):
        print(project)

    print("\nEducation:")
    for education in parsed_resume.get("education", []):
        print(education)

    print("\nEvidence:")
    for evidence in parsed_resume.get("evidence", []):
        print(evidence)


    # ========================================================
    # JOB DESCRIPTION
    # ========================================================

    print("\n" + "=" * 60)
    print("JOB DESCRIPTION")
    print("=" * 60)

    parsed_jd = parse_jd(jd)

    print("\nTitle:")
    print(parsed_jd.get("title", ""))

    print("\nRequirements:")
    for requirement in parsed_jd.get("requirements", []):
        print(requirement)

    print("\nRequired Skills:")
    print(parsed_jd.get("required_skills", []))

    print("\nPreferred Skills:")
    print(parsed_jd.get("preferred_skills", []))

    print("\nRequired Years:")
    print(parsed_jd.get("required_years"))

    print("\nExperience Required:")
    print(parsed_jd.get("experience_required"))

    print("\nEducation Required:")
    print(parsed_jd.get("education_required"))

    print("\nSections:")
    for section, items in parsed_jd.get("sections", {}).items():

        print(f"\n{section.upper()}:")

        for item in items:
            print(f"- {item}")


if __name__ == "__main__":
    main()