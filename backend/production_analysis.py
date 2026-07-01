# ==========================================================
# production_analysis.py
# ==========================================================

"""
Production Experience Analysis

This module detects evidence of real-world production
engineering experience from a candidate's profile.

The output is later used inside quality scoring.
"""

import re


# ==========================================================
# Production Keywords
# ==========================================================

PRODUCTION_KEYWORDS = {

    "production",
    "deployed",
    "deployment",
    "productionized",
    "serving",
    "inference",
    "real users",
    "live system",
    "live systems",
    "pipeline",
    "pipelines",
    "microservice",
    "microservices",
    "api",
    "rest api",
    "backend",
    "latency",
    "throughput",
    "scalable",
    "scalability",
    "distributed",
    "distributed systems",
    "monitoring",
    "logging",
    "observability",
    "docker",
    "kubernetes",
    "airflow",
    "ci/cd",
    "continuous integration",
    "continuous deployment",
    "cloud",
    "aws",
    "azure",
    "gcp"

}


# ==========================================================
# AI Product Keywords
# ==========================================================

AI_PRODUCTION_KEYWORDS = {

    "rag",
    "retrieval",
    "semantic search",
    "vector database",
    "faiss",
    "milvus",
    "pinecone",
    "embedding",
    "embeddings",
    "ranking",
    "recommendation",
    "recommendation system",
    "llm",
    "fine tuning",
    "fine-tuning",
    "prompt engineering",
    "agent",
    "agents"

}


# ==========================================================
# Helper
# ==========================================================

def clean_text(text):

    text = text.lower()

    text = re.sub(r"\s+", " ", text)

    return text


# ==========================================================
# Collect Candidate Text
# ==========================================================

def get_production_text(candidate):

    profile = candidate.get("profile", {})

    career = candidate.get("career_history", [])

    summary = profile.get("summary", "")

    descriptions = []

    for job in career:

        descriptions.append(

            job.get(
                "description",
                ""
            )

        )

    combined = "\n".join(

        [summary] + descriptions

    )

    return clean_text(combined)


# ==========================================================
# Production Analysis
# ==========================================================

def calculate_production_score(candidate):
    """
    Detect production engineering experience.

    Returns score between 0-10.
    """

    text = get_production_text(candidate)

    production_matches = {

        keyword

        for keyword in PRODUCTION_KEYWORDS

        if keyword in text

    }

    ai_matches = {

        keyword

        for keyword in AI_PRODUCTION_KEYWORDS

        if keyword in text

    }

    production_score = (

        min(
            len(production_matches),
            10
        )

        * 0.6

        +

        min(
            len(ai_matches),
            5
        )

        * 0.8

    )

    production_score = min(
        production_score,
        10
    )

    return {

        "production_score":
            round(
                production_score,
                2
            ),

        "production_keyword_count":
            len(
                production_matches
            ),

        "ai_production_keyword_count":
            len(
                ai_matches
            ),

        "matched_production_keywords":
            sorted(
                list(
                    production_matches
                )
            ),

        "matched_ai_keywords":
            sorted(
                list(
                    ai_matches
                )
            )

    }


# ==========================================================
# Recent Production Experience
# ==========================================================

def calculate_recent_production_score(candidate):
    """
    Gives slightly more weight to the
    two most recent jobs.
    """

    career = candidate.get(
        "career_history",
        []
    )

    recent_jobs = sorted(

        career,

        key=lambda x:
        x.get(
            "start_date",
            ""
        ),

        reverse=True

    )[:2]

    text = ""

    for job in recent_jobs:

        text += (
            job.get(
                "description",
                ""
            )

            + "\n"
        )

    text = clean_text(text)

    count = sum(

        1

        for keyword

        in PRODUCTION_KEYWORDS

        if keyword in text

    )

    score = min(
        count,
        10
    )

    return {

        "recent_production_score":
            score

    }


# ==========================================================
# Complete Production Features
# ==========================================================

def calculate_production_features(candidate):
    """
    Returns all production related
    features together.
    """

    features = {}

    features.update(

        calculate_production_score(
            candidate
        )

    )

    features.update(

        calculate_recent_production_score(
            candidate
        )

    )

    return features