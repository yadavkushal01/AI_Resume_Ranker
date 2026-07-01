# ==========================================================
# ranking.py
# ==========================================================

import json
import pandas as pd

# ---------------- Feature Engineering ---------------- #

from feature_engineering import (
    extract_basic_features,
    summary_analysis,
    build_candidate_text,
    build_jd_text,
    calculate_ai_skill_strength,
    calculate_retrieval_strength,
    # calculate_role_match,
    # calculate_domain_match,
    # calculate_company_type_score,
    # calculate_recent_experience_score
)

# ---------------- Semantic ---------------- #

from semantic import (
    generate_embedding,
    generate_embeddings,
    calculate_semantic_match
)

# ---------------- Matching ---------------- #

from matching import (
    calculate_role_match,
    calculate_domain_match,
    calculate_matching_features
)

# ---------------- Production ---------------- #

from production_analysis import (
    calculate_production_features
)

# ---------------- Career ---------------- #

from career_analysis import (
    calculate_company_type_score,
    calculate_recent_experience_score,
    calculate_career_features
)

# ---------------- Behaviour ---------------- #

from behavior import (
    calculate_behavior_pipeline
)

# ---------------- Credibility ---------------- #

from credibility import (
    calculate_credibility_features
)

# ---------------- Scoring ---------------- #

from scoring import (
    calculate_scoring_pipeline
)

# ---------------- Review ---------------- #

from review_generator import (
    generate_candidate_review
)


# ==========================================================
# Score One Candidate
# ==========================================================

def score_candidate(
    candidate,
    jd,
    jd_embedding,
    max_ai_strength,
    max_retrieval_strength,
    candidate_embedding=None,
):
    """
    Complete pipeline for scoring
    a single candidate.
    """

    features = {}

    # ------------------------------------------------------
    # Basic Information
    # ------------------------------------------------------

    features["candidate_id"] = candidate["candidate_id"]

    profile = candidate.get("profile", {})

    features["current_title"] = profile.get(
        "current_title",
        "Professional"
    )

    features["years_of_experience"] = profile.get(
        "years_of_experience",
        0
    )

    # ------------------------------------------------------
    # Feature Engineering
    # ------------------------------------------------------

    features.update(
        extract_basic_features(candidate)
    )

    features.update(
        summary_analysis(candidate)
    )

    features.update(
        calculate_ai_skill_strength(candidate)
    )

    features.update(
        calculate_retrieval_strength(candidate)
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

    features.update(
        calculate_company_type_score(
            candidate
        )
    )

    features.update(
        calculate_recent_experience_score(
            candidate
        )
    )

    # ------------------------------------------------------
    # Skill Matching
    # ------------------------------------------------------

    features.update(
        calculate_matching_features(
            candidate,
            jd
        )
    )

    # ------------------------------------------------------
    # Semantic Matching
    # ------------------------------------------------------

    if candidate_embedding is None:
        candidate_text = build_candidate_text(
            candidate
        )

        candidate_embedding = generate_embedding(
            candidate_text
        )

    features.update(
        calculate_semantic_match(
            candidate_embedding,
            jd_embedding
        )
    )

    # ------------------------------------------------------
    # Production Analysis
    # ------------------------------------------------------

    features.update(
        calculate_production_features(
            candidate
        )
    )

    # ------------------------------------------------------
    # Career Analysis
    # ------------------------------------------------------

    features.update(
        calculate_career_features(
            candidate
        )
    )

    # ------------------------------------------------------
    # Behaviour Analysis
    # ------------------------------------------------------

    features.update(
        calculate_behavior_pipeline(
            candidate
        )
    )

    # ------------------------------------------------------
    # Credibility Analysis
    # ------------------------------------------------------

    features.update(
        calculate_credibility_features(
            candidate
        )
    )

    # ------------------------------------------------------
    # Calculate Final Scores
    # ------------------------------------------------------

    features.update(
        calculate_scoring_pipeline(
            features,
            max_ai_strength,
            max_retrieval_strength
        )
    )

    # ------------------------------------------------------
    # Recruiter Review
    # ------------------------------------------------------

    features["reasoning"] = generate_candidate_review(
        features
    )

    return features

# ==========================================================
# Rank Candidates
# ==========================================================

def rank_candidates(candidates, jd):
    """
    Rank all candidates for a given Job Description.
    """

    # ------------------------------------------------------
    # Build JD embedding once
    # ------------------------------------------------------

    jd_text = build_jd_text(jd)

    jd_embedding = generate_embedding(
        jd_text
    )

    candidate_texts = [
        build_candidate_text(candidate)
        for candidate in candidates
    ]

    candidate_embeddings = generate_embeddings(candidate_texts)

    results = []

    # ------------------------------------------------------
    # Dataset Maximums
    # (Required for normalization)
    # ------------------------------------------------------

    max_ai_strength = 1
    max_retrieval_strength = 1

    for candidate in candidates:

        ai_features = calculate_ai_skill_strength(
            candidate
        )

        retrieval_features = calculate_retrieval_strength(
            candidate
        )

        max_ai_strength = max(

            max_ai_strength,

            ai_features.get(
                "normalized_ai_skill_strength",
                ai_features.get(
                    "normalised_ai_skill_strength",
                    0
                )
            )

        )

        max_retrieval_strength = max(

            max_retrieval_strength,

            retrieval_features.get(
                "normalized_retrieval_strength",
                0
            )

        )

    # ------------------------------------------------------
    # Score Every Candidate
    # ------------------------------------------------------

    for index, candidate in enumerate(candidates):

        candidate_embedding = None

        if len(candidate_embeddings) > index:
            candidate_embedding = candidate_embeddings[index]

        candidate_result = score_candidate(

            candidate,

            jd,

            jd_embedding,

            max_ai_strength,

            max_retrieval_strength,

            candidate_embedding

        )

        results.append(
            candidate_result
        )

    # ------------------------------------------------------
    # Sort Candidates
    # ------------------------------------------------------

    results.sort(

        key=lambda x: (

            -x["score"],

            -x.get(
                "jd_score",
                0
            ),

            -x.get(
                "quality_score",
                0
            ),

            x["candidate_id"]

        )

    )

    # ------------------------------------------------------
    # Assign Ranks
    # ------------------------------------------------------

    for rank, candidate in enumerate(

        results,

        start=1

    ):

        candidate["rank"] = rank

    return results

# ==========================================================
# Save Submission
# ==========================================================

def save_submission(
    results,
    filename="submission.csv",
    top_k=100
):
    """
    Save the ranked candidates
    in the required submission format.
    """

    submission = results[:top_k]

    rows = []

    for candidate in submission:

        rows.append({

            "candidate_id":
                candidate["candidate_id"],

            "rank":
                candidate["rank"],

            "score":
                round(
                    candidate["score"],
                    4
                ),

            "reasoning":
                candidate["reasoning"]

        })

    df = pd.DataFrame(rows)

    df.to_csv(

        filename,

        index=False

    )

    print(
        f"\nSaved {len(df)} candidates to {filename}"
    )

    return df

