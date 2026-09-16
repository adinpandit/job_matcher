import re


# ============================================================
# CANONICAL SKILLS
# ============================================================
#
# These are the official skill names used throughout JobDay.
#
# IMPORTANT:
# - Resume skills should be normalized to these names.
# - JD skills should be normalized to these names.
# - Exact matching should compare these canonical names.
# - Semantic matching can use the original evidence text.
#

SKILLS = [

    # --------------------------------------------------------
    # Programming Languages
    # --------------------------------------------------------

    "python",
    "java",
    "c++",
    "javascript",
    "typescript",

    # --------------------------------------------------------
    # Backend / Web Frameworks
    # --------------------------------------------------------

    "react",
    "next.js",
    "node.js",
    "express",
    "fastapi",
    "django",
    "flask",

    # --------------------------------------------------------
    # Databases
    # --------------------------------------------------------

    "sql",
    "postgresql",
    "mysql",
    "mongodb",
    "redis",

    # --------------------------------------------------------
    # Infrastructure
    # --------------------------------------------------------

    "docker",
    "kubernetes",

    # --------------------------------------------------------
    # Cloud
    # --------------------------------------------------------

    "aws",
    "azure",
    "gcp",

    # --------------------------------------------------------
    # Development Tools
    # --------------------------------------------------------

    "git",
    "github",
    "linux",

    # --------------------------------------------------------
    # Frontend
    # --------------------------------------------------------

    "html",
    "css",
    "tailwind",

    # --------------------------------------------------------
    # Machine Learning
    # --------------------------------------------------------

    "tensorflow",
    "pytorch",
    "scikit-learn",
    "pandas",
    "numpy",

    # --------------------------------------------------------
    # Generative AI
    # --------------------------------------------------------

    "llms",
    "prompt engineering",
    "rag",
    "graphrag",
    "langchain",
    "langgraph",
    "embeddings",

    # --------------------------------------------------------
    # Retrieval / Vector Search
    # --------------------------------------------------------

    "chromadb",
    "faiss",
    "bm25",

    # --------------------------------------------------------
    # NLP / Graph
    # --------------------------------------------------------

    "networkx",
    "spacy",
    "nlp",

    # --------------------------------------------------------
    # APIs / Engineering
    # --------------------------------------------------------

    "openai",
    "rest apis",
    "webhooks",
    "ci/cd",
    "observability",

    # --------------------------------------------------------
    # Vector / Knowledge Systems
    # --------------------------------------------------------

    "vector databases",
    "knowledge graphs",
]


# ============================================================
# SKILL ALIASES
# ============================================================
#
# Different ways candidates/JDs may write the same skill.
#
# Format:
#
#     "alias": "canonical skill"
#
# Example:
#
#     "sklearn" -> "scikit-learn"
#
# Do NOT use aliases for technologies that are merely related.
#
# For example:
#
#     docker != kubernetes
#     git != github
#     sql != postgresql
#     postgresql != mysql
#     llms != openai
#

SKILL_ALIASES = {

    # --------------------------------------------------------
    # Python / ML
    # --------------------------------------------------------

    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",

    # --------------------------------------------------------
    # JavaScript
    # --------------------------------------------------------

    "nextjs": "next.js",
    "next js": "next.js",

    "nodejs": "node.js",
    "node js": "node.js",

    "reactjs": "react",
    "react js": "react",

    # --------------------------------------------------------
    # Databases
    # --------------------------------------------------------

    "postgres": "postgresql",
    "mongo": "mongodb",

    # --------------------------------------------------------
    # Kubernetes
    # --------------------------------------------------------

    "k8s": "kubernetes",

    # --------------------------------------------------------
    # Generative AI
    # --------------------------------------------------------

    "graph rag": "graphrag",

    "lang chain": "langchain",
    "lang graph": "langgraph",

    # --------------------------------------------------------
    # Vector / Retrieval
    # --------------------------------------------------------

    "chroma": "chromadb",

    # --------------------------------------------------------
    # APIs
    # --------------------------------------------------------

    "rest api": "rest apis",

}


# ============================================================
# VALIDATE SKILL CONFIGURATION
# ============================================================

def _validate_skills() -> None:
    """
    Validate the skill configuration when the module loads.

    This catches configuration mistakes early.
    """

    canonical_skills = set(SKILLS)

    # Check duplicate canonical skills.
    if len(SKILLS) != len(canonical_skills):
        raise ValueError(
            "Duplicate skill found in SKILLS."
        )

    # Check aliases point to valid canonical skills.
    for alias, canonical_skill in SKILL_ALIASES.items():

        if canonical_skill not in canonical_skills:
            raise ValueError(
                f"Alias '{alias}' points to unknown "
                f"canonical skill '{canonical_skill}'."
            )


_validate_skills()


# ============================================================
# PATTERN COMPILER
# ============================================================

def compile_skill_pattern(skill: str) -> re.Pattern:
    """
    Create a case-insensitive regex for a skill.

    The boundaries prevent partial matches.

    Example:

        "java" should match:
            Java

        but should NOT match:
            JavaScript
    """

    return re.compile(
        rf"(?<!\w){re.escape(skill)}(?!\w)",
        re.IGNORECASE,
    )


# ============================================================
# CANONICAL SKILL PATTERNS
# ============================================================

PATTERNS = [
    (
        skill,
        compile_skill_pattern(skill),
    )
    for skill in SKILLS
]


# ============================================================
# ALIAS PATTERNS
# ============================================================

ALIAS_PATTERNS = [
    (
        alias,
        canonical_skill,
        compile_skill_pattern(alias),
    )
    for alias, canonical_skill in SKILL_ALIASES.items()
]


# ============================================================
# FIND SKILLS
# ============================================================

def find_skills(text: str) -> list[str]:
    """
    Find skills mentioned in a piece of text.

    Both canonical skill names and aliases are supported.

    Returns:
        A sorted list of canonical skill names.

    Example:

        Input:
            "Experienced with Python, FastAPI, K8s and sklearn."

        Output:
            [
                "fastapi",
                "kubernetes",
                "python",
                "scikit-learn"
            ]
    """

    if not text:
        return []

    if not isinstance(text, str):
        raise TypeError(
            f"find_skills() expected str, "
            f"got {type(text).__name__}"
        )

    found_skills = set()

    # --------------------------------------------------------
    # Search canonical skills
    # --------------------------------------------------------

    for skill, pattern in PATTERNS:

        if pattern.search(text):
            found_skills.add(skill)

    # --------------------------------------------------------
    # Search aliases
    # --------------------------------------------------------

    for alias, canonical_skill, pattern in ALIAS_PATTERNS:

        if pattern.search(text):
            found_skills.add(canonical_skill)

    return sorted(found_skills)


# ============================================================
# NORMALIZE SKILL
# ============================================================

def normalize_skill(skill: str) -> str | None:
    """
    Normalize a single skill to its canonical name.

    Example:

        normalize_skill("SKLEARN")
            -> "scikit-learn"

        normalize_skill("NextJS")
            -> "next.js"

        normalize_skill("Python")
            -> "python"
    """

    if not skill:
        return None

    normalized = skill.lower().strip()

    # Normalize whitespace.
    normalized = re.sub(
        r"\s+",
        " ",
        normalized,
    )

    # Direct canonical skill.
    if normalized in SKILLS:
        return normalized

    # Alias.
    if normalized in SKILL_ALIASES:
        return SKILL_ALIASES[normalized]

    return None


# ============================================================
# NORMALIZE SKILLS
# ============================================================

def normalize_skills(skills: list[str]) -> list[str]:
    """
    Normalize a list of skills to canonical names.

    Unknown skills are ignored.

    Example:

        Input:
            [
                "Python",
                "SKLearn",
                "NextJS",
                "Docker"
            ]

        Output:
            [
                "docker",
                "next.js",
                "python",
                "scikit-learn"
            ]
    """

    if not skills:
        return []

    normalized_skills = set()

    for skill in skills:

        canonical_skill = normalize_skill(skill)

        if canonical_skill:
            normalized_skills.add(canonical_skill)

    return sorted(normalized_skills)