import re

from app.skills import find_skills


# ============================================================
# SECTION ALIASES
# ============================================================

SECTION_ALIASES = {
    "summary": [
        "summary",
        "professional summary",
        "profile",
        "objective",
    ],

    "skills": [
        "skills",
        "technical skills",
        "technologies",
        "core competencies",
    ],

    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment",
    ],

    "projects": [
        "projects",
        "personal projects",
        "academic projects",
    ],

    "education": [
        "education",
        "academic background",
        "academics",
    ],

    "certifications": [
        "certifications",
        "certificates",
    ],

    "achievements": [
        "achievements",
        "accomplishments",
        "awards",
        "awards and achievements",
        "honors",
        "honours",
        "honors and awards",
    ],
}


# ============================================================
# NORMALIZED SECTION ALIASES
# ============================================================

NORMALIZED_SECTION_ALIASES = {
    section: {
        re.sub(r"[^a-z0-9\s]", " ", alias.lower()).strip()
        for alias in aliases
    }
    for section, aliases in SECTION_ALIASES.items()
}


# ============================================================
# SECTION HEADING NORMALIZATION
# ============================================================

def normalize_heading(text: str) -> str:
    """
    Normalize a possible resume section heading.

    Examples:

        "Technical Skills:" -> "technical skills"
        "EXPERIENCE"        -> "experience"
        "Education -"       -> "education"
    """

    text = text.lower()

    # Keep letters, numbers and spaces.
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Collapse multiple spaces.
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# SECTION IDENTIFICATION
# ============================================================

def identify_section(line: str) -> str | None:
    """
    Identify whether a line is a known resume section heading.
    """

    normalized = normalize_heading(line)

    for section_name, aliases in NORMALIZED_SECTION_ALIASES.items():

        if normalized in aliases:
            return section_name

    return None


# ============================================================
# BULLET CLEANING
# ============================================================

def clean_bullet(line: str) -> str:
    """
    Remove common bullet characters and numbering.
    """

    line = line.strip()

    # Remove bullet characters.
    line = re.sub(
        r"^[•●▪◦‣*\-–—]+\s*",
        "",
        line,
    )

    # Remove numbered bullets.
    line = re.sub(
        r"^\d+[.)]\s*",
        "",
        line,
    )

    return line.strip()


# ============================================================
# OCR BULLET NORMALIZATION
# ============================================================

# Bullet markers as they come out of PDF text or OCR:
#   "•", "●", "▪", "◦", "‣", "∙"   real bullet glyphs
#   "«", "»", "¢", "¢«"             common OCR misreads of "•"
#   "e", "o", "e«"                  OCR misreads followed by a space
#   "*", "+", "-", "–", "—"         text bullets followed by a space
#
# The marker must be followed by the start of a sentence (capital letter,
# digit, bracket or quote) so ordinary words are never stripped.

OCR_BULLET_PATTERN = re.compile(
    r"^\s*"
    r"(?:[•●▪◦‣∙«»¢]+\s*|(?:[eo][«»¢]*|[*+\-–—])\s+)"
    r"(?=[A-Z0-9(\"'])"
)

# "Tech: ...", "Stack: ...", "Challenge: ..." at the start of a line.
LABEL_LINE_PATTERN = re.compile(r"^[A-Z][A-Za-z &/+]{1,25}:\s")

# A wrapped line usually breaks after one of these.
CONNECTOR_END_PATTERN = re.compile(
    r"(?:[,(/&+]|\b(?:and|or|with|using|of|for|to|in|on|at|by|via|from|the|a|an))$",
    re.IGNORECASE,
)

# A bullet line at least this fraction of the longest line reaches the
# right margin, so the next line is treated as its continuation.
FULL_WIDTH_RATIO = 0.75


def normalize_bullet_marker(line: str) -> tuple[str, bool]:
    """
    Replace any recognized bullet marker with "• ".

    Returns (line, is_bullet).
    """

    if OCR_BULLET_PATTERN.match(line):
        return "• " + OCR_BULLET_PATTERN.sub("", line, count=1).strip(), True

    return line, False


def is_bullet_continuation(
    previous_physical_line: str,
    line: str,
    longest_line_length: int,
) -> bool:
    """
    Decide whether a non-bullet line continues the previous bullet.
    """

    # Never merge headings, "Tech:" style lines or project titles
    # that follow a complete sentence.
    if identify_section(line):
        return False

    if LABEL_LINE_PATTERN.match(line):
        return False

    if previous_physical_line.endswith((".", "!", "?")):
        return False

    # "reasoning." / "(PR + commit SHA) ..." continue the sentence.
    if line[0].islower() or line[0] in "([&%":
        return True

    if CONNECTOR_END_PATTERN.search(previous_physical_line):
        return True

    # "... plus a graph (spaCy" / "NER + NetworkX) to capture ...": the
    # previous line ran to the right margin. Short lines without sentence
    # punctuation look like titles ("Search Engine GitHub"), so they are
    # never merged this way.
    reached_margin = len(previous_physical_line) >= FULL_WIDTH_RATIO * longest_line_length
    looks_like_sentence_tail = line.endswith((".", "!", "?", ",", ";", ")")) or len(line.split()) >= 8

    return reached_margin and looks_like_sentence_tail


def reconstruct_lines(text: str) -> list[str]:
    """
    Normalize OCR bullet markers and join wrapped bullet lines.

    A blank line always ends a bullet. Only lines that directly follow a
    bullet (or its continuation) can be merged into it.
    """

    raw_lines = [line.strip() for line in text.splitlines()]

    longest_line_length = max(
        (len(line) for line in raw_lines if line),
        default=0,
    )

    lines = []
    inside_bullet = False
    previous_physical_line = ""

    for line in raw_lines:

        if not line:
            inside_bullet = False
            continue

        line, is_bullet = normalize_bullet_marker(line)

        if (
            not is_bullet
            and inside_bullet
            and lines
            and is_bullet_continuation(
                previous_physical_line,
                line,
                longest_line_length,
            )
        ):
            lines[-1] = f"{lines[-1]} {line}"
            previous_physical_line = line
            continue

        lines.append(line)
        inside_bullet = is_bullet
        previous_physical_line = line

    return lines


# ============================================================
# PARSE SECTIONS
# ============================================================

def parse_sections(text: str) -> dict[str, list[str]]:
    """
    Split resume text into sections.

    Each section is stored as a list of lines. OCR bullet markers are
    normalized to "• " and wrapped bullet lines are joined first, so each
    bullet is one line.

    Example:

        {
            "skills": [
                "Python, C++, SQL",
                "FastAPI, Docker, Git"
            ],
            "projects": [
                "• Built an AI resume matcher..."
            ]
        }
    """

    sections = {
        "other": []
    }

    current_section = "other"

    for line in reconstruct_lines(text):

        detected_section = identify_section(line)

        if detected_section:

            current_section = detected_section

            if current_section not in sections:
                sections[current_section] = []

            continue

        sections[current_section].append(line)

    return sections


# ============================================================
# INFER MISSING EXPERIENCE SECTION
# ============================================================

JOB_TITLE_PATTERN = re.compile(
    r"\b(?:intern|internship|engineer|developer|analyst|scientist|consultant|"
    r"associate|architect|researcher|assistant|specialist|manager|designer|"
    r"programmer|trainee|fellow|lead)\b",
    re.IGNORECASE,
)

DATE_PATTERN = re.compile(
    r"\b(?:19|20)\d{2}\b|\bpresent\b|\bcurrent\b|"
    r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s+(?:19|20)\d{2}\b",
    re.IGNORECASE,
)

# "Title — Company", "Title | Company", "Title @ Company", "Title at Company".
COMPANY_SEPARATOR_PATTERN = re.compile(
    r"\s[—–|@-]\s*[A-Z]|\sat\s+[A-Z]",
)


def is_experience_header(line: str, next_line: str | None) -> bool:
    """
    A role header needs a job-title term, a date or a "Title — Company"
    separator, and must be followed by a bullet.
    """

    if not line or line.startswith("• ") or len(line.split()) > 15:
        return False

    if not JOB_TITLE_PATTERN.search(line):
        return False

    if not (DATE_PATTERN.search(line) or COMPANY_SEPARATOR_PATTERN.search(line)):
        return False

    return bool(next_line and next_line.startswith("• "))


def infer_missing_experience(
    sections: dict[str, list[str]],
) -> dict[str, list[str]]:
    """
    Recover experience entries that landed in "other" because the
    EXPERIENCE heading was lost (e.g. cropped scan or OCR miss).

    Only runs when no experience section was detected. Moves each role
    header and the bullets directly under it; everything else stays in
    "other".
    """

    if sections.get("experience"):
        return sections

    other = sections.get("other", [])

    remaining = []
    experience = []
    index = 0

    while index < len(other):

        line = other[index]
        next_line = other[index + 1] if index + 1 < len(other) else None

        if is_experience_header(line, next_line):

            experience.append(line)
            index += 1

            while index < len(other) and other[index].startswith("• "):
                experience.append(other[index])
                index += 1

            continue

        remaining.append(line)
        index += 1

    if experience:
        sections["other"] = remaining
        sections["experience"] = experience

    return sections


# ============================================================
# NAME EXTRACTION
# ============================================================

def extract_name(text: str) -> str:
    """
    Conservatively extract the candidate's name.

    Usually the first meaningful line of a resume
    is the candidate's name.
    """

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return ""

    for line in lines[:5]:

        # Don't use section headings.
        if identify_section(line):
            continue

        # Don't use email.
        if "@" in line:
            continue

        # Don't use LinkedIn.
        if "linkedin" in line.lower():
            continue

        # Don't use GitHub.
        if "github" in line.lower():
            continue

        # Don't use phone numbers.
        if re.search(
            r"\+?\d[\d\s\-()]{7,}",
            line,
        ):
            continue

        words = line.split()

        # Reasonable name length.
        if 1 < len(words) <= 5:

            # Avoid lines containing too many digits.
            if sum(char.isdigit() for char in line) > 2:
                continue

            return line

    return ""


# ============================================================
# CONTACT INFORMATION
# ============================================================

def extract_contact(text: str) -> dict:
    """
    Extract basic contact information.
    """

    email = ""
    phone = ""
    linkedin = ""
    github = ""

    # --------------------------------------------------------
    # Email
    # --------------------------------------------------------

    email_match = re.search(
        r"\b[A-Za-z0-9._%+-]+@"
        r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        text,
    )

    if email_match:
        email = email_match.group(0)

    # --------------------------------------------------------
    # Phone
    # --------------------------------------------------------

    phone_match = re.search(
        r"(?<!\d)(?:\+91[\s\-]?)?"
        r"[6-9]\d{4}[\s\-]?\d{5}(?!\d)",
        text,
    )

    if phone_match:
        phone = phone_match.group(0)

    # --------------------------------------------------------
    # LinkedIn
    # --------------------------------------------------------

    # The profile path stops at whitespace, brackets and separators so that
    # "[www.linkedin.com/in/x](https://...)" or "linkedin.com/in/x | github..."
    # yield only the profile.
    linkedin_match = re.search(
        r"(?:https?://)?(?:www\.)?"
        r"linkedin\.com/[^\s\[\]()<>|,;]+",
        text,
        re.IGNORECASE,
    )

    if linkedin_match:
        linkedin = linkedin_match.group(0).rstrip(".")

    # --------------------------------------------------------
    # GitHub
    # --------------------------------------------------------

    github_match = re.search(
        r"(?:https?://)?(?:www\.)?"
        r"github\.com/[^\s\[\]()<>|,;]+",
        text,
        re.IGNORECASE,
    )

    if github_match:
        github = github_match.group(0).rstrip(".")

    return {
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
    }


def is_header_line(line: str, name: str, contact: dict) -> bool:
    """
    True for the candidate's name line or a line carrying contact details.

    These are metadata, not evidence, so they are kept out of the evidence list.
    """

    stripped = line.strip()

    if name and stripped == name:
        return True

    return any(
        value and value.lower() in stripped.lower()
        for value in contact.values()
    )


# ============================================================
# RESUME SKILLS
# ============================================================

def extract_resume_skills(
    skills_section: list[str],
    full_text: str,
) -> list[str]:
    """
    Extract canonical skills from the resume.

    First searches the explicit Skills section.

    Then searches the complete resume so that skills
    mentioned inside experience/projects are also detected.
    """

    skills = set()

    # --------------------------------------------------------
    # Explicit Skills Section
    # --------------------------------------------------------

    for line in skills_section:

        if not line:
            continue

        found = find_skills(line)

        skills.update(found)

    # --------------------------------------------------------
    # Entire Resume
    # --------------------------------------------------------

    found = find_skills(full_text)

    skills.update(found)

    return sorted(skills)


# ============================================================
# BUILD EXPERIENCE EVIDENCE
# ============================================================

def build_experience_evidence(
    experience: list[str],
) -> list[dict]:
    """
    Convert experience lines into matcher-ready evidence.
    """

    evidence = []

    for item in experience:

        text = clean_bullet(item)

        if not text:
            continue

        skills = find_skills(text)

        evidence_item = {
            "text": text,
            "type": "experience",
            "source": "experience",
        }

        if skills:
            evidence_item["skills"] = skills

        evidence.append(evidence_item)

    return evidence


# ============================================================
# BUILD PROJECT EVIDENCE
# ============================================================

def build_project_evidence(
    projects: list[str],
) -> list[dict]:
    """
    Convert project lines into matcher-ready evidence.
    """

    evidence = []

    for item in projects:

        text = clean_bullet(item)

        if not text:
            continue

        skills = find_skills(text)

        evidence_item = {
            "text": text,
            "type": "project",
            "source": "project",
        }

        if skills:
            evidence_item["skills"] = skills

        evidence.append(evidence_item)

    return evidence


# ============================================================
# EDUCATION EVIDENCE
# ============================================================

def build_education_evidence(
    education: list[str],
) -> list[dict]:
    """
    Convert education lines into structured evidence.
    """

    evidence = []

    for item in education:

        text = clean_bullet(item)

        if not text:
            continue

        evidence.append({
            "text": text,
            "type": "education",
            "source": "education",
        })

    return evidence


# ============================================================
# SUMMARY EVIDENCE
# ============================================================

def build_summary_evidence(
    summary: list[str],
) -> list[dict]:
    """
    Convert summary lines into matcher-ready evidence.
    """

    evidence = []

    for item in summary:

        text = clean_bullet(item)

        if not text:
            continue

        skills = find_skills(text)

        evidence_item = {
            "text": text,
            "type": "summary",
            "source": "summary",
        }

        if skills:
            evidence_item["skills"] = skills

        evidence.append(evidence_item)

    return evidence


# ============================================================
# OTHER SECTION EVIDENCE
# ============================================================

def build_other_evidence(
    other: list[str],
) -> list[dict]:
    """
    Preserve useful text that did not fall under a recognized
    section.

    This is especially useful for resumes where OCR fails to
    detect a section heading.
    """

    evidence = []

    for item in other:

        text = clean_bullet(item)

        if not text:
            continue

        skills = find_skills(text)

        evidence_item = {
            "text": text,
            "type": "other",
            "source": "other",
        }

        if skills:
            evidence_item["skills"] = skills

        evidence.append(evidence_item)

    return evidence


# ============================================================
# MAIN RESUME PARSER
# ============================================================

def parse_resume(text: str) -> dict:
    """
    Parse a resume into structured, matcher-ready data.

    Output contains:

        name
        contact
        sections
        skills
        evidence
        experience
        projects
        education
        certifications
        achievements
    """

    # --------------------------------------------------------
    # Empty Input
    # --------------------------------------------------------

    if not text:

        return {
            "name": "",

            "contact": {
                "email": "",
                "phone": "",
                "linkedin": "",
                "github": "",
            },

            "sections": {
                "other": []
            },

            "skills": [],

            "evidence": [],

            "experience": [],
            "projects": [],
            "education": [],
            "certifications": [],
            "achievements": [],
        }

    # --------------------------------------------------------
    # Parse Sections
    # --------------------------------------------------------

    sections = parse_sections(text)

    # Recover experience whose heading was lost in extraction.
    sections = infer_missing_experience(sections)

    # --------------------------------------------------------
    # Basic Information
    # --------------------------------------------------------

    name = extract_name(text)

    contact = extract_contact(text)

    # --------------------------------------------------------
    # Skills
    # --------------------------------------------------------

    resume_skills = extract_resume_skills(
        sections.get("skills", []),
        text,
    )

    # --------------------------------------------------------
    # Evidence
    # --------------------------------------------------------

    evidence = []

    evidence.extend(
        build_summary_evidence(
            sections.get("summary", [])
        )
    )

    evidence.extend(
        build_experience_evidence(
            sections.get("experience", [])
        )
    )

    evidence.extend(
        build_project_evidence(
            sections.get("projects", [])
        )
    )

    evidence.extend(
        build_education_evidence(
            sections.get("education", [])
        )
    )

    # Name/contact lines live in "other" but are not evidence.
    evidence.extend(
        build_other_evidence(
            [
                line
                for line in sections.get("other", [])
                if not is_header_line(line, name, contact)
            ]
        )
    )

    # --------------------------------------------------------
    # Return Structured Resume
    # --------------------------------------------------------

    return {
        "name": name,

        "contact": contact,

        # Original parsed sections.
        "sections": sections,

        # Canonical skills.
        "skills": resume_skills,

        # Evidence used by matching.
        "evidence": evidence,

        # Individual sections.
        "experience": sections.get(
            "experience",
            [],
        ),

        "projects": sections.get(
            "projects",
            [],
        ),

        "education": sections.get(
            "education",
            [],
        ),

        "certifications": sections.get(
            "certifications",
            [],
        ),

        "achievements": sections.get(
            "achievements",
            [],
        ),
    }