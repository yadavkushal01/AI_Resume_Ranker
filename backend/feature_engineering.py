# ==========================================================
# feature_engineering.py
# Part 1
# ==========================================================

import re


# ==========================================================
# Skill Categories
# ==========================================================

AI_SKILLS = {
    "nlp",
    "fine-tuning llms",
    "speech recognition",
    "tts",
    "lora",
    "gans",
    "image classification"
}

CLOUD_SKILLS = {
    "aws",
    "azure",
    "gcp"
}

RETRIEVAL_SKILLS = {
    "milvus",
    "faiss",
    "pinecone",
    "weaviate",
    "chroma"
}

ENGINEERING_SKILLS = {
    "flask",
    "apache beam"
}


# ==========================================================
# Summary Keywords
# ==========================================================

AI_KEYWORDS = {
    "machine learning",
    "ml project",
    "deep learning",
    "llm",
    "nlp",
    "fine-tuning"
}

RETRIEVAL_KEYWORDS = {
    "retrieval",
    "vector database",
    "semantic search",
    "embedding",
    "ranking",
    "milvus"
}

DATA_ENGINEERING_KEYWORDS = {
    "spark",
    "airflow",
    "etl",
    "warehouse",
    "kafka",
    "data pipeline"
}

AI_INTENT_KEYWORDS = {
    "transitioning toward ai",
    "interested in ai",
    "learning ml",
    "ml focused"
}


# ==========================================================
# Feature Extraction
# ==========================================================

def extract_basic_features(candidate):
    """
    Extract basic structured profile information.

    Returns:
        Dictionary of profile level features.
    """

    profile = candidate.get("profile", {})
    career_history = candidate.get("career_history", [])
    education = candidate.get("education", [])
    skills = candidate.get("skills", [])

    redrob_signal = candidate.get("rebrob_signals", {})

    ai_skill_count = 0
    retrieval_skill_count = 0
    cloud_skill_count = 0
    engineering_skill_count = 0

    skill_names = []

    for skill in skills:

        skill_name = skill.get("name", "").lower().strip()

        skill_names.append(skill_name)

        if skill_name in AI_SKILLS:
            ai_skill_count += 1

        if skill_name in RETRIEVAL_SKILLS:
            retrieval_skill_count += 1

        if skill_name in CLOUD_SKILLS:
            cloud_skill_count += 1

        if skill_name in ENGINEERING_SKILLS:
            engineering_skill_count += 1

    features = {

        "candidate_id":
            candidate.get("candidate_id", ""),

        "current_title":
            profile.get("current_title", ""),

        "current_company":
            profile.get("current_company", ""),

        "years_of_experience":
            profile.get("years_of_experience", 0),

        "headline":
            profile.get("headline", ""),

        "summary":
            profile.get("summary", ""),

        "job_count":
            len(career_history),

        "education_count":
            len(education),

        "skill_names":
            skill_names,

        "num_skills":
            len(skills),

        "ai_skill_count":
            ai_skill_count,

        "retrieval_skill_count":
            retrieval_skill_count,

        "cloud_skill_count":
            cloud_skill_count,

        "engineering_skill_count":
            engineering_skill_count,

        "profile_completeness":
            redrob_signal.get(
                "profile_completeness_score",
                0
            ),

        "github_score":
            redrob_signal.get(
                "github_activity_score",
                0
            ),

        "interview_completion":
            redrob_signal.get(
                "interview_completion_rate",
                0
            )
    }

    return features


# ==========================================================
# Summary Analysis
# ==========================================================

def summary_analysis(candidate):
    """
    Analyze profile summary using keyword matching.

    Returns:
        Dictionary containing keyword frequencies.
    """

    profile = candidate.get("profile", {})

    summary = (
        profile
        .get("summary", "")
        .lower()
    )

    summary = re.sub(r"\s+", " ", summary)

    features = {

        "ai_keywords_count":

            sum(
                1
                for keyword in AI_KEYWORDS
                if keyword in summary
            ),

        "retrieval_keywords_count":

            sum(
                1
                for keyword in RETRIEVAL_KEYWORDS
                if keyword in summary
            ),

        "data_engineering_keywords_count":

            sum(
                1
                for keyword in DATA_ENGINEERING_KEYWORDS
                if keyword in summary
            ),

        "ai_intent_keywords_count":

            sum(
                1
                for keyword in AI_INTENT_KEYWORDS
                if keyword in summary
            )
    }

    return features

# ==========================================================
# Skill Strength Calculation
# ==========================================================

PROFICIENCY_MAP = {
    "beginner": 1,
    "intermediate": 2,
    "advanced": 3
}


AI_SKILL_WEIGHTS = {

    "nlp": 5,
    "fine-tuning llms": 5,
    "speech recognition": 4,
    "lora": 4,
    "tts": 3,
    "image classification": 3,
    "gans": 2

}


RETRIEVAL_SKILL_WEIGHTS = {

    "retrieval": 5,
    "retrieval systems": 5,
    "vector database": 5,
    "vector databases": 5,
    "milvus": 5,
    "faiss": 5,
    "pinecone": 5,
    "weaviate": 5,
    "chroma": 5,
    "embedding": 4,
    "embeddings": 4,
    "semantic search": 4,
    "ranking": 4,
    "ranking systems": 4

}


# ==========================================================
# AI Skill Strength
# ==========================================================

def calculate_ai_skill_strength(candidate):
    """
    Calculate weighted AI skill strength using

    • proficiency
    • endorsements
    • experience duration

    Returns both raw and normalized score.
    """

    skills = candidate.get("skills", [])

    total_strength = 0.0

    for skill in skills:

        skill_name = skill.get("name", "").lower().strip()

        if skill_name not in AI_SKILL_WEIGHTS:
            continue

        proficiency_score = PROFICIENCY_MAP.get(
            skill.get("proficiency", "").lower(),
            0
        )

        endorsement_bonus = (
            skill.get("endorsements", 0) / 10
        )

        experience_bonus = (
            skill.get("duration_months", 0) / 12
        )

        base_strength = (
            proficiency_score +
            endorsement_bonus +
            experience_bonus
        )

        weighted_strength = (
            base_strength *
            AI_SKILL_WEIGHTS[skill_name]
        )

        total_strength += weighted_strength

    normalized_strength = total_strength / 5

    return {

        "ai_skill_strength":
            round(total_strength, 2),

        "normalized_ai_skill_strength":
            round(normalized_strength, 2)

    }


# ==========================================================
# Retrieval Skill Strength
# ==========================================================

def calculate_retrieval_strength(candidate):
    """
    Calculate weighted Retrieval Engineering strength.

    Uses

    • proficiency
    • endorsements
    • duration

    for every retrieval-related skill.
    """

    skills = candidate.get("skills", [])

    total_strength = 0.0

    for skill in skills:

        skill_name = skill.get("name", "").lower().strip()

        if skill_name not in RETRIEVAL_SKILL_WEIGHTS:
            continue

        proficiency_score = PROFICIENCY_MAP.get(
            skill.get("proficiency", "").lower(),
            0
        )

        endorsement_bonus = (
            skill.get("endorsements", 0) / 10
        )

        experience_bonus = (
            skill.get("duration_months", 0) / 12
        )

        base_strength = (
            proficiency_score +
            endorsement_bonus +
            experience_bonus
        )

        weighted_strength = (
            base_strength *
            RETRIEVAL_SKILL_WEIGHTS[skill_name]
        )

        total_strength += weighted_strength

    normalized_strength = total_strength / 5

    return {

        "retrieval_skill_strength":
            round(total_strength, 2),

        "normalized_retrieval_strength":
            round(normalized_strength, 2)

    }

# ==========================================================
# Text Construction for Semantic Matching
# ==========================================================

def build_candidate_text(candidate):
    """
    Build a structured textual representation of a candidate
    for semantic embedding.
    """

    profile = candidate.get("profile", {})
    career_history = candidate.get("career_history", [])
    education = candidate.get("education", [])
    skills = candidate.get("skills", [])

    current_title = profile.get("current_title", "").lower()
    headline = profile.get("headline", "").lower()
    summary = profile.get("summary", "").lower()

    skill_names = [
        skill.get("name", "").lower()
        for skill in skills
    ]

    recent_experience = sorted(
        career_history,
        key=lambda x: x.get("start_date", ""),
        reverse=True
    )[:2]

    experience_descriptions = [
        experience.get("description", "").lower()
        for experience in recent_experience
        if experience.get("description")
    ]

    education_text = [
        " ".join(
            filter(
                None,
                [
                    edu.get("degree", ""),
                    edu.get("field_of_study", ""),
                    edu.get("institution", "")
                ]
            )
        ).lower()
        for edu in education
    ]

    sections = []

    if current_title:
        sections.append(f"Title:\n{current_title}")

    if headline:
        sections.append(f"Headline:\n{headline}")

    if summary:
        sections.append(f"Summary:\n{summary}")

    if skill_names:
        sections.append(
            "Skills:\n" + ", ".join(skill_names)
        )

    if experience_descriptions:
        sections.append(
            "Recent Experience:\n" +
            "\n".join(experience_descriptions)
        )

    if education_text:
        sections.append(
            "Education:\n" +
            "\n".join(education_text)
        )

    return "\n\n".join(sections)


# ==========================================================
# Job Description Text Construction
# ==========================================================

def build_jd_text(jd):
    """
    Build a structured text representation of the
    Job Description for semantic embedding.
    """

    job_title = jd.get("job_title", "").lower()

    job_description = jd.get(
        "job_description",
        ""
    ).lower()

    required_skills = [
        skill.lower()
        for skill in jd.get("required_skills", [])
    ]

    preferred_skills = [
        skill.lower()
        for skill in jd.get("preferred_skills", [])
    ]

    sections = []

    if job_title:
        sections.append(
            f"Job Title:\n{job_title}"
        )

    if job_description:
        sections.append(
            f"Job Description:\n{job_description}"
        )

    if required_skills:
        sections.append(
            "Required Skills:\n" +
            ", ".join(required_skills)
        )

    if preferred_skills:
        sections.append(
            "Preferred Skills:\n" +
            ", ".join(preferred_skills)
        )

    return "\n\n".join(sections)
