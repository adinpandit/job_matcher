from app.skills import find_skills


def extract_jd_skills(sections: dict) -> dict:

    requirements_text = sections.get("requirements", "")
    preferred_text = sections.get("preferred", "")

    return {
        "required_skills": find_skills(requirements_text),
        "preferred_skills": find_skills(preferred_text),
    }
