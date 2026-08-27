SKILL_ALIASES = {
    # Python
    "python": "python",
    "py": "python",
    "python3": "python",

    # Java
    "java": "java",
    "java se": "java",
    "java ee": "java",

    # C++
    "c++": "c++",
    "cpp": "c++",
    "cplusplus": "c++",

    # JavaScript
    "javascript": "javascript",
    "js": "javascript",
    "ecmascript": "javascript",

    # TypeScript
    "typescript": "typescript",
    "ts": "typescript",

    # React
    "react": "react",
    "reactjs": "react",
    "react.js": "react",

    # Next.js
    "next.js": "next.js",
    "nextjs": "next.js",
    "next": "next.js",

    # Node.js
    "node.js": "node.js",
    "nodejs": "node.js",
    "node": "node.js",

    # Express
    "express": "express",
    "express.js": "express",
    "expressjs": "express",

    # FastAPI
    "fastapi": "fastapi",
    "fast api": "fastapi",

    # Django
    "django": "django",

    # Flask
    "flask": "flask",

    # SQL
    "sql": "sql",
    "structured query language": "sql",

    # PostgreSQL
    "postgresql": "postgresql",
    "postgres": "postgresql",
    "psql": "postgresql",

    # MySQL
    "mysql": "mysql",
    "my sql": "mysql",

    # MongoDB
    "mongodb": "mongodb",
    "mongo": "mongodb",
    "mongo db": "mongodb",

    # Redis
    "redis": "redis",

    # Docker
    "docker": "docker",
    "docker container": "docker",

    # Kubernetes
    "kubernetes": "kubernetes",
    "k8s": "kubernetes",
    "kube": "kubernetes",

    # AWS
    "aws": "aws",
    "amazon web services": "aws",

    # Azure
    "azure": "azure",
    "microsoft azure": "azure",

    # GCP
    "gcp": "gcp",
    "google cloud": "gcp",
    "google cloud platform": "gcp",

    # Git
    "git": "git",

    # GitHub
    "github": "github",
    "git hub": "github",

    # Linux
    "linux": "linux",
    "gnu linux": "linux",

    # HTML
    "html": "html",
    "html5": "html",

    # CSS
    "css": "css",
    "css3": "css",

    # Tailwind
    "tailwind": "tailwind",
    "tailwindcss": "tailwind",
    "tailwind css": "tailwind",

    # TensorFlow
    "tensorflow": "tensorflow",
    "tensorflow.js": "tensorflow",
    "tf": "tensorflow",

    # PyTorch
    "pytorch": "pytorch",
    "torch": "pytorch",

    # Scikit-learn
    "scikit-learn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "sklearn": "scikit-learn",

    # Pandas
    "pandas": "pandas",

    # NumPy
    "numpy": "numpy",
    "np": "numpy",
}

def normalize_skills(skills:list[str])->list[str]:
    normalized_skills = []

    for skill in skills:
        skill = skill.lower().strip()

        if skill in SKILL_ALIASES:
            skill = SKILL_ALIASES[skill]
            normalized_skills.append(skill)

        if skill not in SKILL_ALIASES:
            normalized_skills.append(skill)

    return normalized_skills