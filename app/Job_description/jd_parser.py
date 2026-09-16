import re

SECTION_ALIASES = {
    "requirements": [
        "requirements",
        "required qualifications",
        "required skills",
        "minimum qualifications",
        "qualifications",
        "must have",
        "must-have",
        "what we're looking for",
        "what we are looking for",
    ],

    "preferred": [
        "preferred",
        "preferred qualifications",
        "preferred skills",
        "nice to have",
        "nice-to-have",
        "good to have",
        "bonus",
        "additional qualifications",
    ],

    "responsibilities": [
        "responsibilities",
        "job responsibilities",
        "what you'll do",
        "what you will do",
        "duties",
        "role responsibilities",
        "key responsibilities",
    ],

    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "years of experience",
        "relevant experience",
    ],

    "education": [
        "education",
        "educational qualifications",
        "academic qualifications",
        "degree",
        "qualification",
    ],
}

def normalize_heading(text: str) -> str:
    """
    Normalize a heading so that different formatting styles
    can be compared reliably.
    """

    if not text:
        return ""

    text = text.lower().strip()

    # Remove markdown heading markers
    text = re.sub(r"^#+\s*", "", text)

    # Remove bullets
    text = re.sub(r"^[•●▪◦*-]\s*", "", text)

    # Remove trailing colon
    text = re.sub(r":\s*$", "", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()

NORMALIZED_SECTION_ALIASES = {}

for section, aliases in SECTION_ALIASES.items():
    for alias in aliases:
        NORMALIZED_SECTION_ALIASES[normalize_heading(alias)] = section

def identify_section(line: str):
    """
    Return the canonical section name if the line is a known
    section heading.

    Otherwise return None.
    """

    normalized = normalize_heading(line)

    if normalized in NORMALIZED_SECTION_ALIASES:
        return NORMALIZED_SECTION_ALIASES[normalized]

    return None

def clean_bullet(text: str) -> str:
    """
    Remove bullet markers and unnecessary whitespace.
    """

    if not text:
        return ""

    text = text.strip()

    # Common bullet characters
    text = re.sub(
        r"^[•●▪◦○■□‣⁃*+\-]\s*",
        "",
        text
    )

    return text.strip()

def parse_sections(text: str) -> dict[str, list[str]]:
    """
    Split a JD into logical sections.

    Returns:

    {
        "requirements": [...],
        "preferred": [...],
        "responsibilities": [...],
        "experience": [...],
        "education": [...],
        "other": [...]
    }
    """

    sections = {
        "requirements": [],
        "preferred": [],
        "responsibilities": [],
        "experience": [],
        "education": [],
        "other": [],
    }

    if not text:
        return sections

    current_section = "other"

    for raw_line in text.splitlines():

        line = raw_line.strip()

        if not line:
            continue

        section = identify_section(line)

        if section:
            current_section = section
            continue

        cleaned = clean_bullet(line)

        if cleaned:
            sections[current_section].append(cleaned)

    return sections

EXPLICIT_TITLE_PATTERN = re.compile(
    r"^\s*(?:job\s+title|position(?:\s+title)?|role|title)\s*[:\-–—]\s*(.+?)\s*$",
    re.IGNORECASE,
)

# "We are / We're looking for an X", "Seeking an X", "Hiring an X", ...
# The title ends before a connector word or punctuation.
INTRO_TITLE_PATTERN = re.compile(
    r"\b(?:looking\s+for|seeking|hiring|searching\s+for)\s+(?:an?|the)\s+"
    r"(.+?)"
    r"(?=\s+(?:to|who|that|which|with|for|in|at|on|join|joining)\b|[.,;:!]|$)",
    re.IGNORECASE,
)

METADATA_PATTERN = re.compile(
    r"\b(location|salary|remote|hybrid|full[- ]?time|part[- ]?time)\b",
    re.IGNORECASE,
)

ROLE_TERM_PATTERN = re.compile(
    r"\b(?:intern|internship|trainee|apprentice|fellow|engineer|engineering|"
    r"developer|programmer|analyst|scientist|researcher|architect|designer|"
    r"manager|lead|director|head|specialist|consultant|administrator|"
    r"associate|coordinator|technician|officer|executive|strategist|writer|"
    r"sre|devops)\b",
    re.IGNORECASE,
)

# Words that belong to sentences, not job titles.
SENTENCE_WORD_PATTERN = re.compile(
    r"\b(?:we|we're|our|you|your|will|would|who|which|that|is|are|be)\b",
    re.IGNORECASE,
)

MAX_TITLE_WORDS = 8


def looks_like_job_title(candidate: str, require_role_term: bool = True) -> bool:
    """
    Lightweight sanity check for an extracted title.

    Rejects sentence fragments ("right candidate", "Build and maintain ...")
    while accepting ordinary titles ("AI/ML Backend Engineering Intern").
    """

    candidate = candidate.strip()

    if not candidate or not 1 <= len(candidate.split()) <= MAX_TITLE_WORDS:
        return False

    if candidate.endswith((".", "!", "?", ",", ";", ":")):
        return False

    if normalize_heading(candidate) in NORMALIZED_SECTION_ALIASES:
        return False

    if SENTENCE_WORD_PATTERN.search(candidate):
        return False

    if require_role_term:
        return bool(ROLE_TERM_PATTERN.search(candidate))

    return True


def extract_job_title(text: str) -> str:
    """
    Try to extract the job title.

    Priority:
    1. Explicit label: "Job Title: X", "Position: X", "Role: X", "Title: X".
    2. Opening phrase: "We are looking for / seeking / hiring an X ...".
    3. The first meaningful line, when it is itself a title.
    4. Fallback: a short, non-sentence line before the first section heading.
    """

    if not text:
        return ""

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return ""

    # 1. Explicit title label
    for line in lines[:15]:

        match = EXPLICIT_TITLE_PATTERN.match(line)

        if match and looks_like_job_title(match.group(1), require_role_term=False):
            return match.group(1).strip()

    # 2. Opening phrase
    for line in lines[:15]:

        for match in INTRO_TITLE_PATTERN.finditer(line):

            if looks_like_job_title(match.group(1)):
                return match.group(1).strip()

    # 3. First meaningful line is itself a title
    if not METADATA_PATTERN.search(lines[0]) and looks_like_job_title(lines[0]):
        return lines[0]

    # 4. Short line before the first section heading
    for line in lines[:10]:

        # Lines after a section heading are requirements or
        # responsibilities, not the title.
        if normalize_heading(line) in NORMALIZED_SECTION_ALIASES:
            break

        if METADATA_PATTERN.search(line):
            continue

        if looks_like_job_title(line, require_role_term=False):
            return line

    return ""


# ============================================================
# EXPERIENCE YEARS
# ============================================================

EXPERIENCE_PATTERNS = [
    # 2 years
    r"(\d+(?:\.\d+)?)\s*\+?\s*years?",

    # 2-4 years
    r"(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)\s*years?",

    # minimum 2 years
    r"(?:minimum|min\.?|at least)\s*(\d+(?:\.\d+)?)\s*years?",

    # 2+ years
    r"(\d+(?:\.\d+)?)\s*\+\s*years?",
]


# A number of years stated as a requirement:
# "2 years", "2+ years", "0–2 years", "2-4 yrs", "at least 2 years".
# "10 years old" / "5 years ago" are not experience requirements.

YEARS_REQUIREMENT_PATTERN = re.compile(
    r"\b\d+(?:\.\d+)?\s*"
    r"(?:\+|[-–—]\s*\d+(?:\.\d+)?)?\s*\+?\s*"
    r"(?:years?|yrs?)\b"
    r"(?!\s+(?:old|ago)\b)",
    re.IGNORECASE,
)


def has_years_requirement(text: str) -> bool:
    """
    True only when the text states a numeric number of years.

    "0–2 years of relevant experience"      -> True
    "equivalent to professional experience" -> False
    """

    if not text:
        return False

    return bool(YEARS_REQUIREMENT_PATTERN.search(text))


def extract_experience_range(text: str):
    """
    Extract minimum and maximum years of experience.

    Examples:

    "2 years experience"
        -> (2, 2)

    "2-4 years experience"
        -> (2, 4)

    "3+ years experience"
        -> (3, None)

    "at least 2 years"
        -> (2, None)
    """

    if not text:
        return None

    # First check explicit ranges because they contain
    # two numbers.

    range_match = re.search(
        r"(\d+(?:\.\d+)?)\s*[-–—]\s*(\d+(?:\.\d+)?)\s*years?",
        text,
        re.IGNORECASE,
    )

    if range_match:

        minimum = float(range_match.group(1))
        maximum = float(range_match.group(2))

        return (
            int(minimum) if minimum.is_integer() else minimum,
            int(maximum) if maximum.is_integer() else maximum,
        )

    # Minimum / at least / 3+
    minimum_match = re.search(
        r"(?:minimum|min\.?|at least)?\s*"
        r"(\d+(?:\.\d+)?)\s*\+?\s*years?",
        text,
        re.IGNORECASE,
    )

    if minimum_match:

        minimum = float(minimum_match.group(1))

        open_ended = "+" in minimum_match.group(0) or re.search(
            r"minimum|min\.?|at least",
            minimum_match.group(0),
            re.IGNORECASE,
        )

        if open_ended:
            return (
                int(minimum) if minimum.is_integer() else minimum,
                None,
            )

        return (
            int(minimum) if minimum.is_integer() else minimum,
            int(minimum) if minimum.is_integer() else minimum,
        )

    return None

def find_experience_requirement(sections: dict[str, list[str]]):
    """
    Search JD sections for an experience requirement.

    Returns:

    {
        "minimum_years": 2,
        "maximum_years": 4
    }

    or None.
    """

    search_sections = [
        "experience",
        "requirements",
        "preferred",
    ]

    for section_name in search_sections:

        for text in sections.get(section_name, []):

            if not re.search(
                r"\byears?\b",
                text,
                re.IGNORECASE,
            ):
                continue

            experience_range = extract_experience_range(text)

            if experience_range:

                minimum, maximum = experience_range

                return {
                    "minimum_years": minimum,
                    "maximum_years": maximum,
                }

    return None

EDUCATION_KEYWORDS = [
    "bachelor",
    "bachelors",
    "bachelor's",
    "master",
    "masters",
    "master's",
    "phd",
    "doctorate",
    "degree",
    "undergraduate degree",
    "graduate degree",
    "university degree",
    "college degree",
    "pursuing a degree",
    "currently pursuing",
    "enrolled in",
    "academic qualification",
    "educational qualification",
]


EXPERIENCE_KEYWORDS = [
    "years of experience",
    "year of experience",
    "years experience",
    "year experience",
    "professional experience",
    "work experience",
    "industry experience",
    "relevant experience",
]


SOFT_SKILL_KEYWORDS = [
    "communication",
    "communicating",
    "leadership",
    "teamwork",
    "collaboration",
    "collaborative",
    "problem solving",
    "problem-solving",
    "analytical thinking",
    "critical thinking",
    "time management",
    "adaptability",
    "adaptable",
    "attention to detail",
    "interpersonal",
]


RESPONSIBILITY_KEYWORDS = [
    "build",
    "builds",
    "building",
    "develop",
    "developing",
    "develops",
    "design",
    "designing",
    "implement",
    "implementing",
    "maintain",
    "maintaining",
    "integrate",
    "integrating",
    "create",
    "creating",
    "write",
    "writing",
    "deploy",
    "deploying",
    "monitor",
    "monitoring",
    "manage",
    "managing",
    "work with",
    "collaborate",
    "collaborating",
]


def contains_any_keyword(
    text: str,
    keywords: list[str],
) -> bool:
    """
    Check whether text contains any keyword.
    """

    text_lower = text.lower()

    for keyword in keywords:

        if keyword.lower() in text_lower:
            return True

    return False


def classify_requirement(
    requirement_text: str,
    section: str | None = None,
) -> str:
    """
    Classify a JD requirement.

    Possible values:

    - hard_skill
    - soft_skill
    - education
    - experience_years
    - responsibility
    - general
    """

    if not requirement_text:
        return "general"

    text = requirement_text.strip()

    if contains_any_keyword(text, EDUCATION_KEYWORDS):

        return "education"

    # --------------------------------------------------------
    # 2. EXPERIENCE
    # --------------------------------------------------------

    # A requirement is experience_years only when it states a number
    # of years. "professional experience" alone is not enough.

    if has_years_requirement(text):

        return "experience_years"

    # --------------------------------------------------------
    # 3. RESPONSIBILITIES
    # --------------------------------------------------------
    #
    # If the requirement came from the responsibilities
    # section, trust the section first.
    #

    if section == "responsibilities":

        return "responsibility"

    # --------------------------------------------------------
    # 4. SOFT SKILLS
    # --------------------------------------------------------

    if contains_any_keyword(text, SOFT_SKILL_KEYWORDS):

        return "soft_skill"

    # --------------------------------------------------------
    # 5. HARD SKILLS
    # --------------------------------------------------------
    #
    # Technical requirements such as:
    #
    # Python
    # FastAPI
    # ML
    # PyTorch
    # Docker
    # REST APIs
    # RAG
    #
    # will be detected later through extract_requirement_skills().
    #
    # We intentionally don't hard-code the complete skill
    # vocabulary here.
    #

    return "general"


# ============================================================
# IMPORTANCE
# ============================================================

def get_importance(section: str) -> str:
    """
    Determine whether a requirement is required or preferred.
    """

    if section == "preferred":
        return "preferred"

    if section in {
        "requirements",
        "experience",
        "education",
        "responsibilities",
    }:
        return "required"

    return "required"


# ============================================================
# EXTRACT SKILLS FROM REQUIREMENT
# ============================================================

def extract_requirement_skills(requirement_text: str) -> list[str]:
    """
    Extract canonical skills from a single requirement.

    Uses the project's existing JD skill extractor.
    """

    if not requirement_text:
        return []

    # Local import prevents circular-import problems.
    from app.Job_description.jd_skill_extractor import extract_jd_skills

    sections = {
        "requirements": [requirement_text]
    }

    result = extract_jd_skills(sections)

    return result.get("required_skills", [])


# ============================================================
# BUILD REQUIREMENTS
# ============================================================

def build_requirements(
    sections: dict[str, list[str]],
) -> list[dict]:
    """
    Convert raw JD sections into structured requirements.
    """

    requirements = []

    # --------------------------------------------------------
    # Requirements + Preferred
    # --------------------------------------------------------

    for section_name in [
        "requirements",
        "preferred",
    ]:

        importance = get_importance(section_name)

        for text in sections.get(section_name, []):

            if not text:
                continue

            requirement_type = classify_requirement(
                text,
                section_name,
            )

            item = {
                "text": text,
                "type": requirement_type,
                "importance": importance,
            }

            # Experience
            if requirement_type == "experience_years":

                experience_range = extract_experience_range(text)

                if experience_range:

                    minimum, maximum = experience_range

                    item["minimum_years"] = minimum
                    item["maximum_years"] = maximum

            # Education
            elif requirement_type == "education":

                item["education"] = {
                    "text": text,
                }

            # Technical skill
            else:

                skills = extract_requirement_skills(text)

                if skills:
                    item["skills"] = skills

                    # ------------------------------------------------
                    # IMPORTANT FIX
                    # ------------------------------------------------
                    #
                    # If a requirement contains actual technical
                    # skills, classify it as hard_skill unless it is
                    # clearly another category.
                    #
                    # Example:
                    #
                    # "Knowledge of machine learning concepts and
                    #  libraries such as Scikit-learn or PyTorch."
                    #
                    # -> hard_skill
                    #

                    if requirement_type == "general":
                        item["type"] = "hard_skill"

            requirements.append(item)

    # --------------------------------------------------------
    # Responsibilities
    # --------------------------------------------------------

    for text in sections.get("responsibilities", []):

        if not text:
            continue

        item = {
            "text": text,
            "type": "responsibility",
            "importance": "required",
        }

        skills = extract_requirement_skills(text)

        if skills:
            item["skills"] = skills

        requirements.append(item)

    # --------------------------------------------------------
    # Experience section
    # --------------------------------------------------------

    for text in sections.get("experience", []):

        if not text:
            continue

        requirement_type = classify_requirement(
            text,
            "experience",
        )

        item = {
            "text": text,
            "type": requirement_type,
            "importance": "required",
        }

        if requirement_type == "experience_years":

            experience_range = extract_experience_range(text)

            if experience_range:

                minimum, maximum = experience_range

                item["minimum_years"] = minimum
                item["maximum_years"] = maximum

        requirements.append(item)

    # --------------------------------------------------------
    # Education section
    # --------------------------------------------------------

    for text in sections.get("education", []):

        if not text:
            continue

        item = {
            "text": text,
            "type": "education",
            "importance": "required",
            "education": {
                "text": text,
            },
        }

        requirements.append(item)

    return requirements


# ============================================================
# DEDUPLICATE REQUIREMENTS
# ============================================================

def deduplicate_requirements(
    requirements: list[dict],
) -> list[dict]:
    """
    Remove duplicate requirements while preserving order.
    """

    seen = set()
    unique = []

    for requirement in requirements:

        text = requirement.get("text", "")

        # Normalize for comparison
        key = re.sub(
            r"\s+",
            " ",
            text.lower().strip(),
        )

        if not key:
            continue

        if key in seen:
            continue

        seen.add(key)
        unique.append(requirement)

    return unique


# ============================================================
# EXTRACT REQUIRED / PREFERRED SKILLS
# ============================================================

def extract_all_jd_skills(
    sections: dict[str, list[str]],
) -> dict:
    """
    Extract canonical required and preferred skills.

    Required:
        requirements + responsibilities + experience

    Preferred:
        preferred

    Education is intentionally excluded from skill
    classification here.
    """

    from app.Job_description.jd_skill_extractor import extract_jd_skills

    result = extract_jd_skills(sections)

    required_skills = set(
        result.get("required_skills", [])
    )

    preferred_skills = set(
        result.get("preferred_skills", [])
    )

    # Responsibilities are part of what the candidate must
    # actually be able to do, so their detected technical
    # skills are required.

    for text in sections.get("responsibilities", []):

        if not text:
            continue

        responsibility_result = extract_jd_skills(
            {
                "requirements": [text]
            }
        )

        required_skills.update(
            responsibility_result.get(
                "required_skills",
                [],
            )
        )

    # A skill cannot simultaneously be required and preferred.
    preferred_skills -= required_skills

    return {
        "required_skills": sorted(required_skills),
        "preferred_skills": sorted(preferred_skills),
    }


# ============================================================
# MAIN JD PARSER
# ============================================================

def parse_jd(text: str) -> dict:
    """
    Parse a complete job description.

    Returns a structured dictionary containing:

    - title
    - requirements
    - required_skills
    - preferred_skills
    - required_years
    - experience_required
    - education_required
    - sections
    """

    if not text:
        return {
            "title": "",
            "requirements": [],
            "required_skills": [],
            "preferred_skills": [],
            "required_years": None,
            "experience_required": False,
            "education_required": False,
            "sections": {},
        }

    # --------------------------------------------------------
    # 1. Parse sections
    # --------------------------------------------------------

    sections = parse_sections(text)

    # --------------------------------------------------------
    # 2. Extract title
    # --------------------------------------------------------

    title = extract_job_title(text)

    # --------------------------------------------------------
    # 3. Build structured requirements
    # --------------------------------------------------------

    requirements = build_requirements(sections)

    # --------------------------------------------------------
    # 4. Remove duplicate requirements
    # --------------------------------------------------------

    requirements = deduplicate_requirements(
        requirements
    )

    # --------------------------------------------------------
    # 5. Extract skills
    # --------------------------------------------------------

    skill_result = extract_all_jd_skills(
        sections
    )

    required_skills = skill_result[
        "required_skills"
    ]

    preferred_skills = skill_result[
        "preferred_skills"
    ]

    # --------------------------------------------------------
    # 6. Experience
    # --------------------------------------------------------

    experience_requirement = (
        find_experience_requirement(sections)
    )

    if experience_requirement:

        required_years = (
            experience_requirement["minimum_years"],
            experience_requirement["maximum_years"],
        )

    else:

        required_years = None

    # --------------------------------------------------------
    # 7. Education
    # --------------------------------------------------------

    education_required = bool(
        sections.get("education")
    )

    # Also detect education requirements that are written
    # inside the requirements section.

    if not education_required:

        for requirement in requirements:

            if requirement["type"] == "education":

                education_required = True
                break

    # --------------------------------------------------------
    # 8. Experience flag
    # --------------------------------------------------------

    experience_required = (
        required_years is not None
    )

    # --------------------------------------------------------
    # 9. Final result
    # --------------------------------------------------------

    return {
        "title": title,

        "requirements": requirements,

        "required_skills": required_skills,

        "preferred_skills": preferred_skills,

        "required_years": required_years,

        "experience_required": experience_required,

        "education_required": education_required,

        "sections": sections,
    }