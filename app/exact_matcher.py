from app.resume.resume_skills.skill_normalizer import normalize_skills

def exact_match(
        resume_skills:list[str],
        jd_required_skills:list[str],
        jd_preferred_skills:list[str] | None = None,
)->dict:

    if jd_preferred_skills is None:
        jd_preferred_skills = []

    resume_skills = set(normalize_skills(resume_skills))
    jd_required_skills = set(normalize_skills(jd_required_skills))
    jd_preferred_skills = set(normalize_skills(jd_preferred_skills))

    matched_required = resume_skills & jd_required_skills
    missing_required = jd_required_skills - resume_skills

    matched_preferred = resume_skills & jd_preferred_skills
    missing_preferred = jd_preferred_skills - resume_skills

    if jd_required_skills:
        required_score = (len(matched_required)/len(jd_required_skills))*100
    else:
        required_score = 100.0

    if jd_preferred_skills:
        preferred_score = (len(matched_preferred)/len(jd_preferred_skills))*100
    else:
        preferred_score = 100.0

    return {
        "matched_required":sorted(matched_required),
        "missing_required":sorted(missing_required),

        "matched_preferred":sorted(matched_preferred),
        "missing_preferred":sorted(missing_preferred),

        "required_score":round(required_score,2),
        "preferred_score":round(preferred_score,2)
    }
