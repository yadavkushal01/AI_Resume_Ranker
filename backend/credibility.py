# ==========================================================
# credibility.py
# ==========================================================

"""
Credibility Analysis Module

Responsibilities
----------------
1. Detect inconsistent profiles
2. Detect impossible experience
3. Detect unrealistic skill durations
4. Detect employment overlaps
5. Produce credibility score (0-10)
"""


from datetime import datetime


# ==========================================================
# Helper
# ==========================================================

def parse_date(date_string):
    """
    Parse YYYY-MM date.

    Returns None if parsing fails.
    """

    if not date_string:
        return None

    try:
        return datetime.strptime(
            date_string,
            "%Y-%m"
        )

    except:

        try:
            return datetime.strptime(
                date_string,
                "%Y-%m-%d"
            )

        except:

            return None


# ==========================================================
# Years of Experience Validation
# ==========================================================

def validate_experience(candidate):

    years = candidate.get(
        "profile",
        {}
    ).get(
        "years_of_experience",
        0
    )

    jobs = candidate.get(
        "career_history",
        []
    )

    issues = 0

    if years < 0:
        issues += 1

    if years > 45:
        issues += 1

    if years > 10 and len(jobs) == 0:
        issues += 1

    return {

        "experience_issue_count": issues

    }


# ==========================================================
# Skill Duration Validation
# ==========================================================

def validate_skill_duration(candidate):

    years = candidate.get(
        "profile",
        {}
    ).get(
        "years_of_experience",
        0
    )

    skills = candidate.get(
        "skills",
        []
    )

    issues = 0

    max_months = years * 12

    for skill in skills:

        duration = skill.get(
            "duration_months",
            0
        )

        if duration > max_months + 12:
            issues += 1

    return {

        "skill_duration_issue_count":
            issues

    }


# ==========================================================
# Employment Overlap Detection
# ==========================================================

def validate_employment_overlap(candidate):

    career = candidate.get(
        "career_history",
        []
    )

    issues = 0

    parsed_jobs = []

    for job in career:

        start = parse_date(
            job.get(
                "start_date",
                ""
            )
        )

        end = parse_date(
            job.get(
                "end_date",
                ""
            )
        )

        if start:

            parsed_jobs.append(
                (
                    start,
                    end
                )
            )

    parsed_jobs.sort()

    for i in range(
        len(parsed_jobs) - 1
    ):

        current_end = parsed_jobs[i][1]

        next_start = parsed_jobs[i + 1][0]

        if current_end is None:
            continue

        if current_end > next_start:
            issues += 1

    return {

        "employment_overlap_count":
            issues

    }


# ==========================================================
# Career Timeline Validation
# ==========================================================

def validate_career_timeline(candidate):

    career = candidate.get(
        "career_history",
        []
    )

    issues = 0

    for job in career:

        start = parse_date(
            job.get(
                "start_date",
                ""
            )
        )

        end = parse_date(
            job.get(
                "end_date",
                ""
            )
        )

        if start and end:

            if start > end:
                issues += 1

    return {

        "timeline_issue_count":
            issues

    }


# ==========================================================
# Empty Profile Detection
# ==========================================================

def validate_profile(candidate):

    profile = candidate.get(
        "profile",
        {}
    )

    issues = 0

    if not profile.get(
        "summary"
    ):
        issues += 1

    if not profile.get(
        "headline"
    ):
        issues += 1

    if len(
        candidate.get(
            "skills",
            []
        )
    ) == 0:
        issues += 1

    return {

        "profile_issue_count":
            issues

    }


# ==========================================================
# Credibility Score
# ==========================================================

def calculate_credibility_score(features):
    """
    Calculates credibility score.

    Starts from 10 and deducts
    for inconsistencies.
    """

    issues = (

        features.get(
            "experience_issue_count",
            0
        )

        +

        features.get(
            "skill_duration_issue_count",
            0
        )

        +

        features.get(
            "employment_overlap_count",
            0
        )

        +

        features.get(
            "timeline_issue_count",
            0
        )

        +

        features.get(
            "profile_issue_count",
            0
        )

    )

    score = max(

        0,

        10 - issues * 2

    )

    return {

        "credibility_score":
            score,

        "credibility_issues":
            issues

    }


# ==========================================================
# Complete Credibility Pipeline
# ==========================================================

def calculate_credibility_features(candidate):
    """
    Complete credibility analysis.
    """

    features = {}

    features.update(

        validate_experience(
            candidate
        )

    )

    features.update(

        validate_skill_duration(
            candidate
        )

    )

    features.update(

        validate_employment_overlap(
            candidate
        )

    )

    features.update(

        validate_career_timeline(
            candidate
        )

    )

    features.update(

        validate_profile(
            candidate
        )

    )

    features.update(

        calculate_credibility_score(
            features
        )

    )

    return features