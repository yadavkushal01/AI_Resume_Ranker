import json
import re
from pathlib import Path
from typing import Any


def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_tokens(candidate: dict[str, Any]) -> list[str]:
    profile = candidate.get("profile", {}) if isinstance(candidate.get("profile"), dict) else {}
    headline = str(profile.get("headline", "") or "")
    summary = str(profile.get("summary", "") or "")
    skill_names = [str(skill.get("name", "")).strip() for skill in candidate.get("skills", []) if isinstance(skill, dict)]

    text_parts = [headline, summary, " ".join(skill_names)]
    tokens = []
    for part in text_parts:
        tokens.extend(normalize_text(part).split())
    return list(dict.fromkeys(tokens))


def build_retrieval_index(dataset_path: str | Path, index_path: str | Path | None = None) -> dict[str, Any]:
    source_path = Path(dataset_path)
    index_file = Path(index_path) if index_path is not None else source_path.with_suffix(".index.json")

    index: dict[str, Any] = {"dataset": str(source_path), "entries": []}

    with source_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue

            candidate = json.loads(line)
            tokens = extract_tokens(candidate)
            profile = candidate.get("profile", {}) if isinstance(candidate.get("profile"), dict) else {}
            headline = normalize_text(str(profile.get("headline", "") or ""))
            summary = normalize_text(str(profile.get("summary", "") or ""))
            skill_names = [normalize_text(str(skill.get("name", ""))) for skill in candidate.get("skills", []) if isinstance(skill, dict)]
            index["entries"].append(
                {
                    "candidate_id": candidate.get("candidate_id") or f"row_{line_number}",
                    "tokens": tokens,
                    "headline": headline,
                    "summary": summary,
                    "skill_names": skill_names,
                    "candidate": candidate,
                }
            )

    with index_file.open("w", encoding="utf-8") as handle:
        json.dump(index, handle)

    return index


def retrieve_candidates(job_description: str, dataset_path: str | Path, index_path: str | Path | None = None, top_k: int = 50) -> list[dict[str, Any]]:
    source_path = Path(dataset_path)
    if index_path is None:
        index_path = source_path.with_suffix(".index.json")
    index_path = Path(index_path)

    if not index_path.exists():
        index = build_retrieval_index(source_path, index_path=index_path)
    else:
        with index_path.open("r", encoding="utf-8") as handle:
            index = json.load(handle)

    query_text = normalize_text(job_description)
    query_tokens = set(query_text.split())
    if not query_tokens:
        return []

    scored: list[tuple[float, dict[str, Any]]] = []
    for entry in index.get("entries", []):
        entry_tokens = set(entry.get("tokens", []))
        headline_tokens = set(entry.get("headline", "").split())
        skill_tokens = set(entry.get("skill_names", []))

        overlap = len(query_tokens & entry_tokens)
        headline_overlap = len(query_tokens & headline_tokens)
        skill_overlap = len(query_tokens & skill_tokens)

        if overlap or headline_overlap or skill_overlap:
            score = (overlap * 1.0) + (headline_overlap * 2.5) + (skill_overlap * 2.0)
            scored.append(
                (
                    score,
                    {
                        "candidate_id": entry.get("candidate_id"),
                        "overlap": overlap,
                        "headline_overlap": headline_overlap,
                        "skill_overlap": skill_overlap,
                        "score": round(score, 3),
                        "candidate": entry.get("candidate") or {},
                    },
                )
            )

    scored.sort(key=lambda item: (-item[0], item[1]["candidate_id"]))
    return [item[1] for item in scored[:top_k]]
