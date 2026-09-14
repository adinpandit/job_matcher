from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")

def create_embeddings(texts: dict[str]):

    if not texts:
        return {}

    return model.encode(
        texts,
        convert_to_numpy=True
    )

def build_resume_items(resume:dict)->list[dict]:

    resume_items = []

    experience = resume.get("experience","")
    for item in experience.splitlines():
        if item.strip():
            resume_items.append({
                "type":"experience",
                "text":item.strip()
            })

    projects = resume.get("projects","")
    for item in projects.splitlines():
        if item.strip():
            resume_items.append({
                "type":"project",
                "text":item.strip()
            })

    return resume_items

def build_jd_items(jd:dict)->list[dict]:

    jd_items = []

    requirements = jd.get("sections",{}).get("requirements","")
    for item in requirements.splitlines():
        jd_items.append({
            "type":"requirements",
            "text":item.strip()
        })

    responsibilities = jd.get("sections",{}).get("responsibilities","")
    for item in responsibilities.splitlines():
        jd_items.append({
            "type":"responsibilites",
            "text":item.strip()
        })

    return jd_items

def find_best_match(jd_items:list[dict] , resume_items:list[dict] , threshold:float=0.50) -> list[dict]:

    if not jd_items or not resume_items:
        return []

    jd_text = []

    for item in jd_items:
        jd_text.append(item["text"])

    resume_text = []

    for item in resume_items:
        resume_text.append(item["text"])

    jd_embeddings = create_embeddings(jd_text)
    resume_embeddings = create_embeddings(resume_text)

    similarity_matrix = cosine_similarity(jd_embeddings,resume_embeddings)

    matches = []

    for i,jd_item in enumerate(jd_items):

        best_index = similarity_matrix[i].argmax()

        best_score = float(similarity_matrix[i][best_index])

        best_resume_item = resume_items[best_index]

        matches.append({
            "jd_requirement":jd_item["text"],
            "jd_type":jd_item["type"],

            "resume_evidence":best_resume_item["text"],
            "resume_source":best_resume_item["type"],

            "similarity":round(best_score,3),
            "matched":best_score >= threshold
        })

    return matches


def semantic_match(resume:dict , jd: dict , threshold:float = 0.50)->list[dict]:

    resume_items = build_resume_items(resume)

    jd_items = build_jd_items(jd)

    return find_best_match(jd_items ,resume_items, threshold)
