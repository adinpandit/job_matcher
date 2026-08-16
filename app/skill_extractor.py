SKILLS = {
    "python",
    "java",
    "c++",
    "javascript",
    "typescript",
    "react",
    "next.js",
    "node.js",
    "express",
    "fastapi",
    "django",
    "flask",
    "sql",
    "postgresql",
    "mysql",
    "mongodb",
    "redis",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "git",
    "github",
    "linux",
    "html",
    "css",
    "tailwind",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "pandas",
    "numpy",
}

def extract_skill(resume:dict)->list[str]:
    skills_text = resume.get("skills","")

    if not skills_text:
        return []

    skills = []

    for skill in SKILLS:
        if skill.lower() in skills_text.lower():
            skills.append(skill)

    return skills