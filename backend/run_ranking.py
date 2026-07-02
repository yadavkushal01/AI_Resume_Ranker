# ==========================================================
# main.py
# ==========================================================

import argparse
import json
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent

from ranking import (
    save_submission
)
from fast_rank import rank_candidates_fast


# ==========================================================
# Load Candidates
# ==========================================================

def is_raw_candidate_csv(path: Path) -> bool:
    if not path.exists() or not path.is_file():
        return False

    try:
        frame = pd.read_csv(path, nrows=1)
    except Exception:
        return False

    headers = {column.lower().strip() for column in frame.columns}
    raw_fields = {
        "candidate_id",
        "profile",
        "career_history",
        "education",
        "skills",
        "redrob_signals",
        "certifications",
        "languages",
        "headline",
        "summary",
        "current_title",
        "current_company",
    }

    return bool(headers & raw_fields)


def load_candidates(filename):
    """
    Load candidates from JSONL or CSV.
    """

    path = Path(filename)
    extension = path.suffix.lower()

    if extension == ".jsonl":
        candidates = []

        with path.open("r", encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    candidates.append(json.loads(line))

        return candidates

    if extension == ".csv":
        frame = pd.read_csv(path)
        records = frame.where(pd.notna(frame), None).to_dict(orient="records")
        return [normalize_record(record, index) for index, record in enumerate(records, start=1)]

    raise ValueError(f"Unsupported candidate file format: {extension}")


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

def main(args):

    print("=" * 60)
    print("Loading Candidates...")
    print("=" * 60)

    csv_path = REPO_ROOT / "sorted_candidates.jsonl"
    sorted_jsonl_path = REPO_ROOT / "sorted_candidates.jsonl"
    sorted_typo_path = REPO_ROOT / "sorted_candidtates.jsonl"
    jsonl_path = REPO_ROOT / "candidates.jsonl"

    if is_raw_candidate_csv(csv_path):
        candidates = load_candidates(str(csv_path))
    elif sorted_jsonl_path.exists() and sorted_jsonl_path.is_file():
        candidates = load_candidates(str(sorted_jsonl_path))
    elif sorted_typo_path.exists() and sorted_typo_path.is_file():
        candidates = load_candidates(str(sorted_typo_path))
    elif jsonl_path.exists() and jsonl_path.is_file():
        candidates = load_candidates(str(jsonl_path))
    else:
        raise FileNotFoundError(
            "No valid default candidate dataset found. Provide a raw sorted_candidates.jsonl or candidates.jsonl file."
        )

    print(f"Loaded {len(candidates)} candidates.")

    print("\nRanking candidates...")

    results = rank_candidates_fast(

        candidates,

        JD,

        dataset_path=(sorted_jsonl_path if sorted_jsonl_path.exists() and sorted_jsonl_path.is_file() else sorted_typo_path if sorted_typo_path.exists() and sorted_typo_path.is_file() else jsonl_path),

        cache_path=args.cache_path,

        rebuild_cache=args.rebuild_cache,

    )

    print("Ranking completed.")

    save_submission(

        results,

        filename="submission.csv"

    )

    print("\nSubmission saved successfully!")
    print("=" * 60)


# ==========================================================
# Entry Point
# ==========================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Rank candidates with optional candidate embedding cache."
    )
    parser.add_argument(
        "--cache-path",
        default="backend/candidate_embeddings.npz",
        help="Path to the candidate embedding cache file."
    )
    parser.add_argument(
        "--rebuild-cache",
        action="store_true",
        help="Rebuild and overwrite the candidate embedding cache."
    )
    args = parser.parse_args()
    main(args)