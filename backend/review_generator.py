# ==========================================================
# review_generator.py
# ==========================================================

"""
Review Generator Module

Responsibilities
----------------
1. Generate recruiter-friendly explanations
2. Highlight strengths
3. Mention weaknesses
4. Explain ranking decisions
"""


# ==========================================================
# Strength Extraction
# ==========================================================

def get_strengths(features):

    strengths = []

    if features.get("required_skill_score", 0) >= 8:
        strengths.append("excellent required skill match")

    elif features.get("required_skill_score", 0) >= 6:
        strengths.append("strong required skill match")

    if features.get("preferred_skill_score", 0) >= 6:
        strengths.append("preferred skills aligned")

    if features.get("semantic_score", 0) >= 0.75:
        strengths.append("high semantic similarity")

    elif features.get("semantic_score", 0) >= 0.60:
        strengths.append("good semantic similarity")

    if features.get("production_score", 0) >= 7:
        strengths.append("production AI experience")

    if features.get("recent_production_score", 0) >= 5:
        strengths.append("recent production work")

    if features.get("retrieval_skill_strength", 0) >= 20:
        strengths.append("strong retrieval expertise")

    if features.get("ai_skill_strength", 0) >= 20:
        strengths.append("strong AI background")

    if features.get("career_progression_score", 0) >= 8:
        strengths.append("steady career progression")

    if features.get("education_score", 0) >= 7:
        strengths.append("relevant educational background")

    if features.get("behavior_score", 0) >= 8:
        strengths.append("excellent recruiter engagement")

    if features.get("credibility_score", 10) >= 9:
        strengths.append("high profile credibility")

    return strengths


# ==========================================================
# Weakness Extraction
# ==========================================================

def get_weaknesses(features):

    weaknesses = []

    if features.get("required_skill_score", 0) < 5:
        weaknesses.append("missing several required skills")

    if features.get("semantic_score", 0) < 0.50:
        weaknesses.append("low semantic alignment")

    if features.get("production_score", 0) < 4:
        weaknesses.append("limited production experience")

    if features.get("recent_experience_score", 0) < 4:
        weaknesses.append("recent experience weakly aligned")

    if features.get("career_progression_score", 0) < 4:
        weaknesses.append("limited career progression")

    if features.get("education_score", 0) < 4:
        weaknesses.append("education less relevant")

    if features.get("behavior_score", 0) < 5:
        weaknesses.append("low recruiter engagement")

    if features.get("credibility_score", 10) < 7:
        weaknesses.append("profile has credibility concerns")

    return weaknesses


# ==========================================================
# Recommendation
# ==========================================================

def get_recommendation(score):

    if score >= 0.90:
        return "Highly Recommended"

    if score >= 0.80:
        return "Strongly Recommended"

    if score >= 0.70:
        return "Recommended"

    if score >= 0.60:
        return "Consider"

    return "Low Priority"


# ==========================================================
# Review Generator
# ==========================================================

def generate_candidate_review(features):

    title = features.get(
        "current_title",
        "Professional"
    )

    experience = features.get(
        "years_of_experience",
        0
    )

    strengths = get_strengths(features)

    weaknesses = get_weaknesses(features)

    score = features.get(
        "score",
        0
    )

    recommendation = get_recommendation(score)

    review = []

    # ------------------------------------------------------
    # Introduction
    # ------------------------------------------------------

    review.append(

        f"{title} with "

        f"{experience:.1f} years of experience."

    )

    # ------------------------------------------------------
    # Strengths
    # ------------------------------------------------------

    if strengths:

        review.append(

            "Strengths: "

            + ", ".join(strengths) + "."

        )

    # ------------------------------------------------------
    # Weaknesses
    # ------------------------------------------------------

    if weaknesses:

        review.append(

            "Areas for improvement: "

            + ", ".join(weaknesses) + "."

        )

    # ------------------------------------------------------
    # Recommendation
    # ------------------------------------------------------

    review.append(

        f"Recommendation: {recommendation}."

    )

    return " ".join(review)


# ==========================================================
# Detailed Review (Optional)
# ==========================================================

def generate_detailed_review(features):

    return {

        "candidate_id":
            features.get(
                "candidate_id"
            ),

        "recommendation":
            get_recommendation(
                features.get(
                    "score",
                    0
                )
            ),

        "strengths":
            get_strengths(
                features
            ),

        "weaknesses":
            get_weaknesses(
                features
            ),

        "overall_review":
            generate_candidate_review(
                features
            )

    }