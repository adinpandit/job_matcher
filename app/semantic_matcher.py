from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


# Initial V1 thresholds.
# These should eventually be calibrated using labeled
# resume/JD matching examples.
SEMANTIC_THRESHOLDS = {
    "hard_skill": 0.60,
    "responsibility": 0.55,
    "soft_skill": 0.55,
    "general": 0.55,
    "education": 0.65,
    "experience_years": 0.70,
}


# Small source preference used only for ranking.
# Semantic similarity remains the primary signal.
SOURCE_WEIGHTS = {
    "experience": 1.00,
    "project": 0.95,
    "education": 0.90,
    "achievement": 0.85,
    "skills": 0.80,
    "unknown": 0.80,
}


def create_embeddings(texts: list[str]):
    """
    Create normalized embeddings for a list of texts.

    Normalization allows cosine similarity to be used
    directly and makes the embedding representation
    consistent across retrieval calls.
    """

    if not texts:
        return []

    return model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )


def build_resume_evidence(resume: dict) -> list[dict]:
    """
    Build the semantic-searchable evidence collection
    from the current parsed resume.

    Expected resume structure:

        {
            "evidence": [
                {
                    "text": "...",
                    "type": "experience",
                    "source": "experience",
                    "skills": [...]
                }
            ]
        }
    """

    evidence = resume.get("evidence", [])

    if not evidence:
        return []

    resume_items = []

    for item in evidence:

        text = item.get("text", "").strip()

        if not text:
            continue

        resume_items.append(
            {
                "text": text,
                "type": item.get("type", "unknown"),
                "source": item.get("source", "unknown"),
                "skills": item.get("skills", []),
            }
        )

    return resume_items


def build_jd_requirements(jd: dict) -> list[dict]:
    """
    Build the semantic-searchable JD requirement collection
    from the current parsed JD.

    Expected structure:

        {
            "requirements": [
                {
                    "text": "...",
                    "type": "hard_skill",
                    "importance": "required",
                    "skills": [...]
                }
            ]
        }
    """

    requirements = jd.get("requirements", [])

    if not requirements:
        return []

    jd_items = []

    for index, requirement in enumerate(
        requirements,
        start=1,
    ):

        text = requirement.get("text", "").strip()

        if not text:
            continue

        jd_items.append(
            {
                "id": f"req_{index:03d}",
                "text": text,
                "type": requirement.get(
                    "type",
                    "general",
                ),
                "importance": requirement.get(
                    "importance",
                    "required",
                ),
                "skills": requirement.get(
                    "skills",
                    [],
                ),
            }
        )

    return jd_items


def get_threshold(requirement_type: str) -> float:
    """
    Get the semantic retrieval threshold for a requirement type.
    """

    return SEMANTIC_THRESHOLDS.get(
        requirement_type,
        SEMANTIC_THRESHOLDS["general"],
    )


def get_source_weight(source: str) -> float:
    """
    Get a small ranking preference for the source of evidence.

    This does NOT determine whether evidence satisfies a
    requirement. It only helps rank equally relevant evidence.
    """

    return SOURCE_WEIGHTS.get(
        source,
        SOURCE_WEIGHTS["unknown"],
    )


def calculate_retrieval_score(
    similarity: float,
    source: str,
) -> float:
    """
    Calculate a source-aware retrieval score.

    Similarity remains the primary signal.
    """

    return similarity * get_source_weight(source)


def find_semantic_matches(
    jd_requirements: list[dict],
    resume_evidence: list[dict],
    top_k: int = 3,
) -> list[dict]:
    """
    Retrieve the top-K semantically relevant resume evidence
    for every JD requirement.

    This function performs RETRIEVAL only.

    It does not decide:
        MATCH
        PARTIAL
        MISSING

    That decision belongs to the analyzer layer.
    """

    if not jd_requirements or not resume_evidence:
        return []

    # ------------------------------------------------------
    # Create embedding inputs
    # ------------------------------------------------------

    jd_texts = [
        requirement["text"]
        for requirement in jd_requirements
    ]

    resume_texts = [
        evidence["text"]
        for evidence in resume_evidence
    ]

    # ------------------------------------------------------
    # Generate embeddings
    # ------------------------------------------------------

    jd_embeddings = create_embeddings(jd_texts)

    resume_embeddings = create_embeddings(
        resume_texts
    )

    # ------------------------------------------------------
    # Calculate all JD → Resume similarities
    # ------------------------------------------------------

    similarity_matrix = cosine_similarity(
        jd_embeddings,
        resume_embeddings,
    )

    matches = []

    # ------------------------------------------------------
    # Process every JD requirement independently
    # ------------------------------------------------------

    for requirement_index, requirement in enumerate(
        jd_requirements
    ):

        similarity_scores = similarity_matrix[
            requirement_index
        ]

        threshold = get_threshold(
            requirement["type"]
        )

        # --------------------------------------------------
        # Rank resume evidence
        # --------------------------------------------------

        ranked_indices = sorted(
            range(len(resume_evidence)),
            key=lambda index: calculate_retrieval_score(
                float(similarity_scores[index]),
                resume_evidence[index]["source"],
            ),
            reverse=True,
        )

        top_evidence = []

        # --------------------------------------------------
        # Retrieve top-K evidence
        # --------------------------------------------------

        for resume_index in ranked_indices[:top_k]:

            evidence = resume_evidence[
                resume_index
            ]

            similarity = float(
                similarity_scores[resume_index]
            )

            retrieval_score = calculate_retrieval_score(
                similarity,
                evidence["source"],
            )

            top_evidence.append(
                {
                    "text": evidence["text"],
                    "type": evidence["type"],
                    "source": evidence["source"],
                    "skills": evidence["skills"],
                    "similarity": round(
                        similarity,
                        3,
                    ),
                    "retrieval_score": round(
                        retrieval_score,
                        3,
                    ),
                    "above_threshold": (
                        similarity >= threshold
                    ),
                }
            )

        # --------------------------------------------------
        # Keep only semantically relevant evidence
        # --------------------------------------------------

        relevant_evidence = [
            evidence
            for evidence in top_evidence
            if evidence["above_threshold"]
        ]

        # --------------------------------------------------
        # Best semantic similarity
        # --------------------------------------------------

        if relevant_evidence:

            best_similarity = max(
                evidence["similarity"]
                for evidence in relevant_evidence
            )

        else:

            best_similarity = 0.0

        matches.append(
            {
                "requirement_id": requirement["id"],
                "requirement": requirement["text"],
                "requirement_type": requirement["type"],
                "importance": requirement["importance"],
                "skills": requirement["skills"],

                "threshold": threshold,

                "best_similarity": round(
                    best_similarity,
                    3,
                ),

                "semantic_evidence": relevant_evidence,

                "has_semantic_evidence": bool(
                    relevant_evidence
                ),
            }
        )

    return matches


def semantic_match(
    resume: dict,
    jd: dict,
    top_k: int = 3,
) -> list[dict]:
    """
    Main semantic matching pipeline.

    Parsed Resume
        ↓
    Resume Evidence
        ↓
    Parsed JD
        ↓
    JD Requirements
        ↓
    Embeddings
        ↓
    Cosine Similarity
        ↓
    Top-K Resume Evidence
    """

    resume_evidence = build_resume_evidence(
        resume
    )

    jd_requirements = build_jd_requirements(
        jd
    )

    return find_semantic_matches(
        jd_requirements=jd_requirements,
        resume_evidence=resume_evidence,
        top_k=top_k,
    )