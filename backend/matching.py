# ==========================================================
# matching.py
# ==========================================================

"""
All Job Description matching functions.

This module is responsible for:

1. Skill normalization
2. Required skill matching
3. Preferred skill matching
4. Role matching
5. Domain matching
"""

# ==========================================================
# Skill Synonyms
# ==========================================================

SKILL_MAP = {

    "milvus": {"vector_database", "retrieval"},
    "faiss": {"vector_database", "retrieval"},
    "pinecone": {"vector_database", "retrieval"},
    "weaviate": {"vector_database", "retrieval"},
    "chroma": {"vector_database", "retrieval"},

    "lora": {"llm"},
    "fine-tuning llms": {"llm"},
    "fine tuning llms": {"llm"},

    "aws": {"cloud"},
    "azure": {"cloud"},
    "gcp": {"cloud"}

}


# ==========================================================
# JD Skill Weights
# ==========================================================

JD_WEIGHTS = {

    "retrieval": 5,
    "ranking": 5,
    "embeddings": 4,
    "embedding": 4,
    "vector_database": 3,
    "python": 3

}


# ==========================================================
# Role Mapping
# ==========================================================

ROLE_MATCH = {

    "retrieval engineer": 10,
    "ml engineer": 9,
    "machine learning engineer": 9,
    "ai engineer": 8,
    "nlp engineer": 7,
    "data scientist": 6,
    "data engineer": 5,
    "backend engineer": 4,
    "software engineer": 3,
    "hr manager": 1

}


# ==========================================================
# Domain Keywords
# ==========================================================

AI_KEYWORDS = {

    "machine learning",
    "deep learning",
    "llm",
    "nlp",
    "fine-tuning"

}

RETRIEVAL_KEYWORDS = {

    "retrieval",
    "semantic search",
    "vector database",
    "embedding",
    "ranking"

}

DATA_ENGINEERING_KEYWORDS = {

    "spark",
    "etl",
    "airflow",
    "warehouse",
    "kafka"

}

AI_INTENT_KEYWORDS = {

    "interested in ai",
    "learning ml",
    "transitioning toward ai",
    "ml focused"

}


# ==========================================================
# Normalize Candidate Skills
# ==========================================================

def normalize_skills(candidate_skills):

    normalized = set()

    for skill in candidate_skills:

        skill = skill.lower().strip()

        normalized.add(skill)

        if skill in SKILL_MAP:

            normalized.update(SKILL_MAP[skill])

    return normalized


# ==========================================================
# Required Skill Match
# ==========================================================

def calculate_required_skill_match(
    candidate_skills,
    required_skills
):

    candidate = normalize_skills(candidate_skills)

    required = {
        skill.lower()
        for skill in required_skills
    }

    matched = candidate.intersection(required)

    if len(required) == 0:

        score = 0

    else:

        score = (
            len(matched)
            /
            len(required)
        ) * 10

    obtained_weight = sum(

        JD_WEIGHTS.get(skill, 0)

        for skill in candidate

    )

    maximum_weight = sum(

        JD_WEIGHTS.get(skill, 0)

        for skill in required

    )

    if maximum_weight == 0:

        weighted_score = 0

    else:

        weighted_score = (
            obtained_weight
            /
            maximum_weight
        ) * 10

    return {

        "matched_required_skills":
            list(matched),

        "required_skill_score":
            round(score, 2),

        "weighted_required_score":
            round(weighted_score, 2)

    }


# ==========================================================
# Preferred Skill Match
# ==========================================================

def calculate_preferred_skill_match(
    candidate_skills,
    preferred_skills
):

    candidate = normalize_skills(candidate_skills)

    preferred = {

        skill.lower()

        for skill in preferred_skills

    }

    matched = candidate.intersection(preferred)

    if len(preferred) == 0:

        score = 0

    else:

        score = (
            len(matched)
            /
            len(preferred)
        ) * 10

    obtained_weight = sum(

        JD_WEIGHTS.get(skill, 0)

        for skill in candidate

    )

    maximum_weight = sum(

        JD_WEIGHTS.get(skill, 0)

        for skill in preferred

    )

    if maximum_weight == 0:

        weighted_score = 0

    else:

        weighted_score = (
            obtained_weight
            /
            maximum_weight
        ) * 10

    return {

        "matched_preferred_skills":
            list(matched),

        "preferred_skill_score":
            round(score, 2),

        "weighted_preferred_score":
            round(weighted_score, 2)

    }


# ==========================================================
# Role Match
# ==========================================================

def calculate_role_match(
    candidate,
    jd
):

    current_title = (

        candidate
        .get("profile", {})
        .get("current_title", "")
        .lower()

    )

    jd_title = (

        jd
        .get("job_title", "")
        .lower()

    )

    candidate_score = ROLE_MATCH.get(
        current_title,
        0
    )

    jd_score = ROLE_MATCH.get(
        jd_title,
        0
    )

    difference = abs(
        candidate_score -
        jd_score
    )

    role_match = max(
        0,
        10 - difference * 2
    )

    return {

        "role_match_score":
            role_match

    }


# ==========================================================
# Domain Match
# ==========================================================

# def calculate_domain_match(candidate):

#     summary = (

#         candidate
#         .get("profile", {})
#         .get("summary", "")
#         .lower()

#     )

#     ai = sum(
#         1
#         for keyword in AI_KEYWORDS
#         if keyword in summary
#     )

#     retrieval = sum(
#         1
#         for keyword in RETRIEVAL_KEYWORDS
#         if keyword in summary
#     )

#     data = sum(
#         1
#         for keyword in DATA_ENGINEERING_KEYWORDS
#         if keyword in summary
#     )

#     intent = sum(
#         1
#         for keyword in AI_INTENT_KEYWORDS
#         if keyword in summary
#     )

#     domain_score = (

#         min(ai, 3)
#         +
#         min(retrieval, 3)
#         +
#         min(intent, 2)
#         +
#         min(data, 2)

#     )

#     return {

#         "domain_match_score":
#             round(domain_score, 2)

#     }

def calculate_domain_match(candidate, jd):
    """
    Compare candidate domains with JD domains.
    """

    from feature_engineering import (build_candidate_text)

    candidate_text = build_candidate_text(candidate).lower()

    jd_text = (
        jd.get("job_title", "") + " " +
        jd.get("job_description", "") + " " +
        " ".join(jd.get("required_skills", [])) + " " +
        " ".join(jd.get("preferred_skills", []))
    ).lower()

    domain_keywords = {
        "retrieval": [
            "retrieval",
            "semantic search",
            "rag",
            "vector",
            "embedding",
            "milvus",
            "pinecone",
            "faiss",
            "chroma"
        ],

        "ranking": [
            "ranking",
            "recommendation",
            "search",
            "relevance"
        ],

        "llm": [
            "llm",
            "gpt",
            "transformer",
            "bert",
            "lora",
            "fine tuning"
        ],

        "ml": [
            "machine learning",
            "deep learning",
            "tensorflow",
            "pytorch",
            "xgboost",
            "lightgbm"
        ],

        "nlp": [
            "nlp",
            "text classification",
            "named entity",
            "tokenization",
            "language model"
        ],

        "vision": [
            "computer vision",
            "image classification",
            "object detection",
            "segmentation"
        ]
    }

    candidate_domains = set()
    jd_domains = set()

    for domain, keywords in domain_keywords.items():

        if any(k in candidate_text for k in keywords):
            candidate_domains.add(domain)

        if any(k in jd_text for k in keywords):
            jd_domains.add(domain)

    if len(jd_domains) == 0:
        score = 0

    else:
        score = len(candidate_domains & jd_domains) / len(jd_domains)

    return {
        "domain_match_score": score,
        "candidate_domains": list(candidate_domains),
        "jd_domains": list(jd_domains)
    }


# ==========================================================
# Combined Matching Features
# ==========================================================

def calculate_matching_features(
    candidate,
    jd
):

    candidate_skills = [

        skill.get("name", "")

        for skill in candidate.get(
            "skills",
            []
        )

    ]

    features = {}

    features.update(

        calculate_required_skill_match(

            candidate_skills,

            jd.get(
                "required_skills",
                []
            )

        )

    )

    features.update(

        calculate_preferred_skill_match(

            candidate_skills,

            jd.get(
                "preferred_skills",
                []
            )

        )

    )

    features.update(

        calculate_role_match(
            candidate,
            jd
        )

    )

    features.update(

        calculate_domain_match(
            candidate,
            jd
        )

    )

    return features