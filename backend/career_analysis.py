# ==========================================================
# career_analysis.py
# ==========================================================

"""
Career Analysis Module

This module evaluates a candidate's professional journey.

Responsibilities
----------------
1. Recent experience relevance
2. Career progression
3. Company type estimation
4. Education relevance
"""

import re
from datetime import datetime


# ==========================================================
# Target Company Keywords
# ==========================================================

PRODUCT_COMPANIES = {

    "google",
    "amazon",
    "microsoft",
    "meta",
    "apple",
    "netflix",
    "uber",
    "airbnb",
    "linkedin",
    "openai",
    "anthropic",
    "nvidia",
    "flipkart",
    "meesho",
    "swiggy",
    "zomato",
    "razorpay",
    "cred",
    "phonepe"

}


SERVICE_COMPANIES = {

    "tcs",
    "infosys",
    "wipro",
    "cognizant",
    "capgemini",
    "accenture",
    "hcl",
    "tech mahindra",
    "persistent"

}


# ==========================================================
# Relevant Experience Keywords
# ==========================================================

RELEVANT_KEYWORDS = {

    "retrieval",
    "ranking",
    "semantic search",
    "embedding",
    "vector database",
    "faiss",
    "milvus",
    "pinecone",
    "rag",
    "llm",
    "nlp",
    "recommendation",
    "search",
    "machine learning",
    "deep learning"

}


# ==========================================================
# Education Keywords
# ==========================================================

EDUCATION_KEYWORDS = {

    "computer science",
    "artificial intelligence",
    "machine learning",
    "data science",
    "information technology",
    "software engineering"

}


# ==========================================================
# Helper
# ==========================================================

def clean_text(text):

    text = text.lower()

    text = re.sub(r"\s+", " ", text)

    return text


# ==========================================================
# Recent Experience
# ==========================================================

def calculate_recent_experience_score(candidate):
    """
    Analyze only the two most recent jobs.
    """

    career = candidate.get(
        "career_history",
        []
    )

    career = sorted(

        career,

        key=lambda x:
        x.get(
            "start_date",
            ""
        ),

        reverse=True

    )[:2]

    text = ""

    for job in career:

        text += (

            job.get(
                "title",
                ""
            )

            + " "

            +

            job.get(
                "description",
                ""
            )

            + "\n"

        )

    text = clean_text(text)

    keyword_count = sum(

        1

        for keyword

        in RELEVANT_KEYWORDS

        if keyword in text

    )

    score = min(

        keyword_count,

        10

    )

    return {

        "recent_experience_score":
            score,

        "recent_relevant_keywords":
            keyword_count

    }


# ==========================================================
# Career Progression
# ==========================================================

def calculate_career_progression_score(candidate):
    """
    Estimate career growth based on
    number of jobs and years of experience.
    """

    profile = candidate.get(
        "profile",
        {}
    )

    years = profile.get(
        "years_of_experience",
        0
    )

    jobs = len(

        candidate.get(
            "career_history",
            []
        )

    )

    score = 0

    if years >= 2:
        score += 2

    if years >= 4:
        score += 2

    if years >= 6:
        score += 2

    if jobs >= 2:
        score += 2

    if jobs >= 4:
        score += 2

    return {

        "career_progression_score":
            min(score, 10)

    }


# ==========================================================
# Company Type
# ==========================================================

def calculate_company_type_score(candidate):
    """
    Estimate company exposure.

    Product companies receive slightly
    higher weight than service companies.
    """

    career = candidate.get(
        "career_history",
        []
    )

    score = 0

    product_count = 0

    service_count = 0

    for job in career:

        company = clean_text(

            job.get(
                "company",
                ""
            )

        )

        if company in PRODUCT_COMPANIES:

            product_count += 1

        elif company in SERVICE_COMPANIES:

            service_count += 1

    score += min(
        product_count * 2,
        8
    )

    score += min(
        service_count,
        2
    )

    return {

        "company_type_score":
            min(score, 10),

        "product_company_count":
            product_count,

        "service_company_count":
            service_count

    }


# ==========================================================
# Education
# ==========================================================

def calculate_education_score(candidate):
    """
    Estimate education relevance.
    """

    education = candidate.get(
        "education",
        []
    )

    score = 0

    relevant = 0

    for degree in education:

        text = clean_text(

            " ".join([

                degree.get(
                    "degree",
                    ""
                ),

                degree.get(
                    "field_of_study",
                    ""
                ),

                degree.get(
                    "institution",
                    ""
                )

            ])

        )

        for keyword in EDUCATION_KEYWORDS:

            if keyword in text:

                relevant += 1

                break

    score = min(
        relevant * 5,
        10
    )

    return {

        "education_score":
            score,

        "relevant_education":
            relevant

    }


# ==========================================================
# Overall Career Features
# ==========================================================

def calculate_career_features(candidate):
    """
    Complete career analysis.
    """

    features = {}

    features.update(

        calculate_recent_experience_score(
            candidate
        )

    )

    features.update(

        calculate_career_progression_score(
            candidate
        )

    )

    features.update(

        calculate_company_type_score(
            candidate
        )

    )

    features.update(

        calculate_education_score(
            candidate
        )

    )

    return features