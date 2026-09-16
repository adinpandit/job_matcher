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

def match_requirements(resume:dict,jd_requirements:list[dict])->list[dict]:

    resume_skills = set(normalize_skills(resume.get("skills",[])))

    resume_evidence = resume.get("evidence",[])

    results = []

    for index,requirement in enumerate(jd_requirements,start = 1):

        requirement_text = requirement.get("text","")
        requirement_type = requirement.get("type","general")
        importance = requirement.get("importance","required")

        requirement_skills = set(normalize_skills(requirement.get("skills",[])))

        matched_skills = requirement_skills & resume_skills
        missing_skills = requirement_skills - resume_skills

        evidence = []

        for item in resume_evidence:

            evidence_skills = set(normalize_skills(item.get("skills",[])))

            matched_evidence_skills = (evidence_skills & matched_skills)

            if matched_skills:

                evidence.append({
                    "text":item.get("text",""),
                    "type":item.get("type"),
                    "source":item.get("source"),
                    "matched_skills":sorted(matched_evidence_skills),
                })
        if not requirement_skills:

            status = "NO_EXACT_SKILLS"

            match_score = None

        elif matched_skills == requirement_skills:

            status = "MATCH"

            match_score = 1.0

        elif matched_skills:

            status = "PARTIAL"

            match_score = (len(matched_skills)/len(requirement_skills))

        else:

            status = "Missing"

            match_score = 0.0

        result = {
            "id": f"req_{index:03d}",

            "text": requirement_text,

            "type": requirement_type,

            "importance": importance,

            "skills": sorted(requirement_skills),

            "exact_match": {
                "matched_skills": sorted(matched_skills),
                "missing_skills": sorted(missing_skills),
            },

            "status": status,

            "match_score": (
                round(match_score, 2)
                if match_score is not None
                else None
            ),

            "evidence": evidence,
        }

        results.append(result)

    return results
                                  