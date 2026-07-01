# ==========================================================
# main.py
# ==========================================================

import json

from ranking import (
    rank_candidates,
    save_submission
)


# ==========================================================
# Load Candidates
# ==========================================================

def load_candidates(filename):
    """
    Load candidates from JSONL file.
    """

    candidates = []

    with open(
        filename,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            if line.strip():

                candidates.append(
                    json.loads(line)
                )

    return candidates


# ==========================================================
# Job Description
# ==========================================================

JD = {

    "job_title": "Retrieval Engineer",

    "job_description": """
    We are looking for a Retrieval Engineer with strong
    experience in Retrieval Systems, Vector Databases,
    Embedding Models, Ranking Systems, Python and Large
    Language Models.

    The candidate should have experience building
    semantic search systems, RAG pipelines and
    scalable AI applications.

    Experience with cloud platforms is preferred.
    """,

    "required_skills": [

        "Python",
        "Retrieval",
        "Vector Database",
        "Embeddings",
        "Ranking"

    ],

    "preferred_skills": [

        "LLM",
        "Fine-Tuning",
        "Cloud"

    ]

}


# ==========================================================
# Main
# ==========================================================

def main():

    print("=" * 60)
    print("Loading Candidates...")
    print("=" * 60)

    candidates = load_candidates(
        "candidates.jsonl"
    )

    print(f"Loaded {len(candidates)} candidates.")

    print("\nRanking candidates...")

    results = rank_candidates(

        candidates,

        JD

    )

    print("Ranking completed.")

    save_submission(

        results,

        filename="submission.csv",

        top_k=100

    )

    print("\nSubmission saved successfully!")
    print("=" * 60)


# ==========================================================
# Entry Point
# ==========================================================

if __name__ == "__main__":
    main()