import json
from pathlib import Path

from backend.fast_retrieval import build_retrieval_index, retrieve_candidates


def test_retrieve_candidates_by_keywords(tmp_path):
    dataset_path = tmp_path / "sorted_candidates.jsonl"
    index_path = tmp_path / "candidate_index.json"

    records = [
        {
            "candidate_id": "c1",
            "profile": {
                "headline": "Senior Python Backend Engineer",
                "summary": "Builds scalable APIs and services",
            },
            "skills": [{"name": "Python"}, {"name": "FastAPI"}],
        },
        {
            "candidate_id": "c2",
            "profile": {
                "headline": "Machine Learning Engineer",
                "summary": "Works with LLMs and embeddings",
            },
            "skills": [{"name": "PyTorch"}, {"name": "LLM"}],
        },
        {
            "candidate_id": "c3",
            "profile": {
                "headline": "Frontend React Developer",
                "summary": "Builds web applications",
            },
            "skills": [{"name": "React"}, {"name": "TypeScript"}],
        },
    ]

    with dataset_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record) + "\n")

    build_retrieval_index(dataset_path, index_path=index_path)
    matches = retrieve_candidates("Python backend engineer", dataset_path, index_path=index_path, top_k=5)

    assert [match["candidate_id"] for match in matches][:1] == ["c1"]


def test_retrieve_candidates_prioritizes_headline_and_skill_matches(tmp_path):
    dataset_path = tmp_path / "sorted_candidates.jsonl"
    index_path = tmp_path / "candidate_index.json"

    records = [
        {
            "candidate_id": "c1",
            "profile": {
                "headline": "Senior Backend Engineer",
                "summary": "Works on infrastructure and support tasks",
            },
            "skills": [{"name": "Python"}, {"name": "FastAPI"}],
        },
        {
            "candidate_id": "c2",
            "profile": {
                "headline": "Cloud Specialist",
                "summary": "Python backend engineer with APIs and cloud",
            },
            "skills": [{"name": "Azure"}],
        },
    ]

    with dataset_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record) + "\n")

    build_retrieval_index(dataset_path, index_path=index_path)
    matches = retrieve_candidates("python backend engineer", dataset_path, index_path=index_path, top_k=5)

    assert matches[0]["candidate_id"] == "c1"
