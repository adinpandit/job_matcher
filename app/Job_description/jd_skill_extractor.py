from app.skills import find_skills


def extract_jd_skills(sections: dict[str, list[str]]) -> dict:
    """
    Extract required and preferred skills from JD sections.

    sections:
        {
            "requirements": [...],
            "preferred": [...],
            "responsibilities": [...],
            ...
        }
    """

    required_skills = set()
    preferred_skills = set()

    # -----------------------------------------
    # Required skills
    # -----------------------------------------

    for text in sections.get("requirements", []):

        if not text:
            continue

        skills = find_skills(text)

        required_skills.update(skills)

    # -----------------------------------------
    # Preferred skills
    # -----------------------------------------

    for text in sections.get("preferred", []):

        if not text:
            continue

        skills = find_skills(text)

        preferred_skills.update(skills)

    return {
        "required_skills": sorted(required_skills),
        "preferred_skills": sorted(preferred_skills),
    }