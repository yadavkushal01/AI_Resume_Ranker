# ==========================================================
# behavior.py
# ==========================================================

"""
Behavior Analysis Module

Responsibilities
----------------
1. Extract recruiter / platform behavior signals
2. Normalize behavioural features
3. Calculate overall behavior score
"""

# ==========================================================
# Feature Extraction
# ==========================================================

def calculate_behavior_features(candidate):
    """
    Extract behavioural features from candidate profile.
    """

    redrob_signals = candidate.get(
        "redrob_signals",
        {}
    )

    profile = candidate.get(
        "profile",
        {}
    )

    features = {

        "profile_completeness":
            redrob_signals.get(
                "profile_completeness_score",
                0
            ),

        "github_score":
            redrob_signals.get(
                "github_activity_score",
                0
            ),

        "interview_completion":
            redrob_signals.get(
                "interview_completion_rate",
                0
            ),

        "recruiter_response_rate":
            redrob_signals.get(
                "recruiter_response_rate",
                0
            ),

        "open_to_work":
            profile.get(
                "open_to_work_flag",
                False
            )

    }

    return features


# ==========================================================
# Behaviour Score
# ==========================================================

def calculate_behavior_score(features):
    """
    Calculate behaviour score.

    Final Range:
        0 - 10
    """

    profile_score = min(

        features.get(
            "profile_completeness",
            0
        ),

        100

    ) / 100

    github_score = min(

        features.get(
            "github_score",
            0
        ),

        10

    ) / 10

    interview_score = min(

        features.get(
            "interview_completion",
            0
        ),

        100

    ) / 100

    recruiter_response = min(

        features.get(
            "recruiter_response_rate",
            0
        ),

        1

    )

    open_to_work = (

        1

        if features.get(
            "open_to_work",
            False
        )

        else 0

    )

    score = (

        interview_score * 3

        +

        github_score * 3

        +

        profile_score * 2

        +

        recruiter_response * 1

        +

        open_to_work * 1

    )

    return {

        "behavior_score":
            round(score, 2)

    }


# ==========================================================
# Complete Behaviour Pipeline
# ==========================================================

def calculate_behavior_pipeline(candidate):
    """
    Complete behaviour analysis.

    Returns
    -------
    Dictionary containing
    extracted features
    +
    behaviour score.
    """

    features = calculate_behavior_features(
        candidate
    )

    score = calculate_behavior_score(
        features
    )

    features.update(score)

    return features