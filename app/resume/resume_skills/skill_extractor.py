from app.skills import SKILLS, find_skills

__all__ = ["SKILLS", "extract_skill"]

def extract_skill(resume:dict)->list[str]:
    skills_text = resume.get("skills","")

    return find_skills(skills_text)