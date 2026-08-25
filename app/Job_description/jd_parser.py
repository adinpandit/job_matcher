import re

SECTION_ALIASES = {
    "requirements": [
        "requirements",
        "qualifications",
        "required qualifications",
        "basic qualifications",
        "minimum qualifications",
        "required skills",
        "must have",
        "must haves",
    ],

    "preferred": [
        "preferred qualifications",
        "preferred skills",
        "preferred requirements",
        "nice to have",
        "nice to have skills",
        "good to have",
    ],

    "responsibilities": [
        "responsibilities",
        "key responsibilities",
        "job responsibilities",
        "what you'll do",
        "what you will do",
        "duties",
        "role responsibilities",
    ],

    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "required experience",
    ],

    "education": [
        "education",
        "educational qualifications",
        "academic qualifications",
        "academic requirements",
    ],

    "benefits": [
        "benefits",
        "perks",
        "what we offer",
    ],
}

def normalize_heading(text:str)->str:
    return re.sub(r"[^a-z ]","",text.lower()).strip();

def identify_sections(line:str):
    normalized=normalize_heading(line)

    for section_name,aliases in SECTION_ALIASES.items():

        normalized_aliases = []

        for alias in aliases:
            normalized_aliases.append(normalize_heading(alias))

        if normalized in normalized_aliases:
            return section_name

    return None

def parse_section(text:str)->str:

    sections = {
        "other":[]
    } 

    current_section = "other"

    for line in text.splitlines():
        line = line.strip()         

        if not line:
            continue

        detected_section = identify_sections(line)

        if detected_section:

            current_section = detected_section

            if current_section not in sections:
                sections[current_section] = []

            continue

        sections[current_section].append(line)

    result = {}

    for section,content in sections.items():
        result[section] = "\n".join(content)

    return result

def extract_required_years(text:str)->int:

    text = text.lower()

    # Range: 0-2 years / 0–2 years / 3-5 years
    range_pattern = (
        r"(\d+)\s*[-–—]\s*(\d+)\s*years?"
    )

    match = re.search(range_pattern,text)

    if match:
        minimum = int(match.group(1))
        maximum = int(match.group(2))

        return minimum , maximum

    # Range: 3 to 5 years
    range_to_pattern = (
        r"(\d+)\s+to\s+(\d+)\s*years?"
    )

    match = re.search(range_to_pattern,text)
    
    if match:
        minimum = int(match.group(1))
        maximum = int(match.group(2))
    
        return minimum , maximum

    # 2+ years
    plus_pattern = (
        r"(\d+)\s*\+\s*years?"
    )

    match = re.search(plus_pattern, text)

    if match:
        minimum = int(match.group(1))

        return minimum, None

    # Minimum 5 years
    minimum_pattern = (
        r"minimum\s+(\d+)\s*years?"
    )

    match = re.search(minimum_pattern, text)

    if match:
        minimum = int(match.group(1))

        return minimum, None

    # At least 2 years
    at_least_pattern = (
        r"at\s+least\s+(\d+)\s*years?"
    )

    match = re.search(at_least_pattern, text)

    if match:
        minimum = int(match.group(1))

        return minimum, None

    # 3 years of experience
    experience_pattern = (
        r"(\d+)\s*years?\s+of\s+experience"
    )

    match = re.search(experience_pattern, text)

    if match:
        minimum = int(match.group(1))

        return minimum, None

    # 3 years experience
    simple_experience_pattern = (
        r"(\d+)\s*years?\s+experience"
    )

    match = re.search(
        simple_experience_pattern,
        text
    )

    if match:
        minimum = int(match.group(1))

        return minimum, None

    return 0, None

def extract_job_title(text:str)->str:

    lines = []

    for line in text.splitlines():
        line = line.strip()
        if line:
            lines.append(line)

    if not lines:
        return ""

    patterns = [
        r"job title\s*:\s*(.+)",
        r"position\s*:\s*(.+)",
        r"role\s*:\s*(.+)",
        r"title\s*:\s*(.+)",
    ]

    for line in lines:
        for pattern in patterns:
            match = re.search(pattern,line,re.IGNORECASE)
            if match:
                return match.group(1).strip()

    for line in lines:
        if len(line) >= 5:
            return line
        
    return line[0]


def parse_jd(text: str) -> dict:
    if not text:

        return {
            "title": "",
            "required_skills": [],
            "preferred_skills": [],
            "min_experience_years":0,
            "max_experience_years":None,
            "experience_required": False,
            "education_required": False,
            "sections": {}
        }

    sections = parse_section(text)

    experience_text = sections.get(
        "experience",
        ""
    )

    requirements_text = sections.get(
        "requirements",
        ""
    )

    education_text = sections.get(
        "education",
        ""
    )

    if not experience_text:
        experience_text = requirements_text

    if not education_text:
        education_text = requirements_text

    min_experience_years,max_experience_years = (extract_required_years(experience_text))

    experience_required = (min_experience_years > 0)

    education_required = bool(education_text)

    return {
        "title": extract_job_title(text),

        "required_skills": [],

        "preferred_skills": [],

        "min_experience_years": min_experience_years,

        "max_experience_years": max_experience_years,

        "experience_required": experience_required,

        "education_required": education_required,

        "sections": sections
    }


        