import re

SKILLS = [
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

    "llms",
    "prompt engineering",
    "rag",
    "graphrag",
    "langchain",
    "langgraph",
    "embeddings",

    "chromadb",
    "faiss",
    "bm25",

    "networkx",
    "spacy",
    "nlp",

    "openai",
    "rest apis",
    "webhooks",
    "ci/cd",
    "observability",

    "vector databases",
    "knowledge graphs",
]


def compile(skill: str) -> re.Pattern:

    return re.compile(rf"(?<!\w){re.escape(skill)}(?!\w)", re.IGNORECASE)


PATTERNS = [(skill, compile(skill)) for skill in SKILLS]


def find_skills(text: str) -> list[str]:
    
    if not text:
        return []

    return [skill for skill, pattern in PATTERNS if pattern.search(text)]
