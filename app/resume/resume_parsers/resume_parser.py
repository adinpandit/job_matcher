import re

section_aliases = {
    "summary":[
        "summary",
        "professional summary",
        "profile",
        "objective"
    ],
    "skills":[
        "skills",
        "technical skills",
        "technologies",
        "core competencies"
    ],
    "experience":[
        "experience",
        "work experience",
        "professional experience",
        "employment"
    ],
    "projects":[
        "projects",
        "personal projects",
        "academic projects"
    ],
    "education":[
        "education",
        "academic background",
        "academics"
    ],
    "certifications":[
        "certifications",
        "certificates"
    ],
    "achievements": [
        "achievements",
        "accomplishments",
        "awards",
        "awards and achievements",
        "honors",
        "honours",
        "honors and awards"
    ],
}

def normalize_heading(text:str)->str:
    return re.sub(r"[^a-z ]","",text.lower()).strip()

def identify_section(line:str):
    normalized = normalize_heading(line)

    for section_name,aliases in section_aliases.items():
        if normalized in aliases:
            return section_name
        
    return None

def parse_resume(text:str)->dict:
    sections = {
        "other":[]
    }

    current_section = "other"

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        detected_section = identify_section(line)

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
