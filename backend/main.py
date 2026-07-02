from __future__ import annotations

import io
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware

BACKEND_DIR = Path(__file__).resolve().parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from matching import normalize_skills
from review_generator import get_recommendation, get_strengths, get_weaknesses

SUPPORTED_EXTENSIONS = {".jsonl", ".json", ".csv", ".xlsx"}
JSON_WRAPPER_FIELDS = ("candidate", "candidate_json", "candidate_payload", "payload", "data")
STRUCTURED_FIELDS = (
    "profile",
    "career_history",
    "education",
    "skills",
    "redrob_signals",
    "certifications",
    "languages",
)
PROFILE_FIELDS = {
    "anonymized_name",
    "headline",
    "summary",
    "location",
    "country",
    "years_of_experience",
    "current_title",
    "current_company",
    "current_company_size",
    "current_industry",
    "open_to_work_flag",
}

RAW_CSV_FIELDS = {
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


def is_raw_candidate_csv(path: Path) -> bool:
    if not path.exists() or not path.is_file():
        return False

    try:
        frame = pd.read_csv(path, nrows=1)
    except Exception:
        return False

    headers = {column.lower().strip() for column in frame.columns}
    return bool(headers & RAW_CSV_FIELDS)
REDROB_FIELDS = {
    "profile_completeness_score",
    "signup_date",
    "last_active_date",
    "open_to_work_flag",
    "profile_views_received_30d",
    "applications_submitted_30d",
    "recruiter_response_rate",
    "avg_response_time_hours",
    "skill_assessment_scores",
    "connection_count",
    "endorsements_received",
    "notice_period_days",
    "expected_salary_range_inr_lpa",
    "preferred_work_mode",
    "willing_to_relocate",
    "github_activity_score",
    "search_appearance_30d",
    "saved_by_recruiters_30d",
    "interview_completion_rate",
    "offer_acceptance_rate",
    "verified_email",
    "verified_phone",
    "linkedin_connected",
}
SKILL_PATTERNS: dict[str, tuple[str, ...]] = {
    "Python": (r"\bpython\b",),
    "Retrieval": (r"\bretrieval\b", r"retrieval systems?"),
    "Vector Database": (
        r"vector databases?",
        r"vector dbs?",
        r"\bfaiss\b",
        r"\bmilvus\b",
        r"\bpinecone\b",
        r"\bweaviate\b",
        r"\bchroma\b",
    ),
    "Embeddings": (r"\bembeddings?\b",),
    "Ranking": (r"\branking\b", r"ranking systems?"),
    "LLM": (r"\bllm\b", r"large language models?", r"\bgpt\b", r"\btransformers?\b"),
    "Fine-Tuning": (r"fine[- ]tuning", r"\blora\b"),
    "Cloud": (r"\bcloud\b", r"\baws\b", r"\bazure\b", r"\bgcp\b"),
    "RAG": (r"\brag\b", r"retrieval augmented generation"),
    "Semantic Search": (r"semantic search",),
    "NLP": (r"\bnlp\b", r"natural language processing"),
    "Machine Learning": (r"machine learning", r"\bml\b"),
    "PyTorch": (r"\bpytorch\b",),
    "TensorFlow": (r"\btensorflow\b",),
    "FastAPI": (r"\bfastapi\b",),
    "Flask": (r"\bflask\b",),
    "Spark": (r"\bspark\b", r"\bpyspark\b"),
    "Airflow": (r"\bairflow\b",),
    "Kafka": (r"\bkafka\b",),
    "SQL": (r"\bsql\b",),
    "Docker": (r"\bdocker\b",),
    "Kubernetes": (r"\bkubernetes\b", r"\bk8s\b"),
    "React": (r"\breact\b",),
    "TypeScript": (r"\btypescript\b", r"\bts\b"),
}
REQUIRED_CUES = ("required", "must", "strong experience", "requirements", "responsibilities")
PREFERRED_CUES = ("preferred", "nice to have", "bonus", "plus", "good to have")

app = FastAPI(
    title="TalentMind AI Resume Ranker API",
    description="FastAPI service for ranking candidate datasets against a pasted job description.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def is_blank_value(value: Any) -> bool:
    if value is None:
        return True

    if isinstance(value, float) and pd.isna(value):
        return True

    if isinstance(value, str) and not value.strip():
        return True

    return False


def decode_text(content: bytes) -> str:
    try:
        return content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="The uploaded file must be UTF-8 encoded.") from exc


def maybe_parse_json(value: Any) -> Any:
    if not isinstance(value, str):
        return value

    stripped = value.strip()

    if not stripped:
        return None

    if stripped[0] not in "[{":
        return value

    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return value


def split_path_tokens(key: str) -> list[str | int]:
    tokens: list[str | int] = []

    for segment in re.finditer(r"([^\.\[\]]+)|\[(\d+)\]", key):
        name = segment.group(1)
        index = segment.group(2)

        if name is not None:
            tokens.append(int(name) if name.isdigit() else name)
        elif index is not None:
            tokens.append(int(index))

    return tokens


def set_nested_value(target: dict[str, Any], key: str, value: Any) -> None:
    tokens = split_path_tokens(key)

    if not tokens:
        return

    cursor: Any = target
    parent: Any = None
    parent_key: str | int | None = None

    for index, token in enumerate(tokens):
        is_last = index == len(tokens) - 1
        next_token = None if is_last else tokens[index + 1]

        if isinstance(token, str):
            if not isinstance(cursor, dict):
                replacement: dict[str, Any] = {}

                if isinstance(parent_key, int):
                    parent[parent_key] = replacement
                elif parent_key is not None:
                    parent[parent_key] = replacement

                cursor = replacement

            if is_last:
                cursor[token] = value
                return

            if token not in cursor or cursor[token] is None:
                cursor[token] = [] if isinstance(next_token, int) else {}

            parent = cursor
            parent_key = token
            cursor = cursor[token]
            continue

        if not isinstance(cursor, list):
            replacement = []

            if isinstance(parent_key, int):
                parent[parent_key] = replacement
            elif parent_key is not None:
                parent[parent_key] = replacement

            cursor = replacement

        while len(cursor) <= token:
            cursor.append(None)

        if is_last:
            cursor[token] = value
            return

        if cursor[token] is None:
            cursor[token] = [] if isinstance(next_token, int) else {}

        parent = cursor
        parent_key = token
        cursor = cursor[token]


def parse_skill_list(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []

    parsed = maybe_parse_json(value)

    if isinstance(parsed, str):
        skill_names = [item.strip() for item in parsed.split(",") if item.strip()]
        return [
            {"name": skill_name, "proficiency": "beginner", "endorsements": 0, "duration_months": 0}
            for skill_name in skill_names
        ]

    if not isinstance(parsed, list):
        return []

    skills: list[dict[str, Any]] = []

    for skill in parsed:
        if isinstance(skill, str):
            skills.append(
                {
                    "name": skill.strip(),
                    "proficiency": "beginner",
                    "endorsements": 0,
                    "duration_months": 0,
                }
            )
            continue

        if isinstance(skill, dict):
            skill_name = str(skill.get("name", "")).strip()

            if not skill_name:
                continue

            skills.append(
                {
                    "name": skill_name,
                    "proficiency": str(skill.get("proficiency", "beginner")).lower() or "beginner",
                    "endorsements": int(skill.get("endorsements", 0) or 0),
                    "duration_months": int(skill.get("duration_months", 0) or 0),
                }
            )

    return skills


def normalize_candidate(candidate: dict[str, Any], index: int) -> dict[str, Any]:
    normalized = dict(candidate)
    profile = normalized.get("profile")

    if not isinstance(profile, dict):
        profile = {}

    normalized["profile"] = profile
    normalized["candidate_id"] = str(normalized.get("candidate_id") or f"UPLOADED_{index:05d}")
    normalized["career_history"] = (
        normalized["career_history"] if isinstance(normalized.get("career_history"), list) else []
    )
    normalized["education"] = (
        normalized["education"] if isinstance(normalized.get("education"), list) else []
    )
    normalized["skills"] = parse_skill_list(normalized.get("skills"))
    normalized["redrob_signals"] = (
        normalized["redrob_signals"] if isinstance(normalized.get("redrob_signals"), dict) else {}
    )
    normalized["certifications"] = (
        normalized["certifications"] if isinstance(normalized.get("certifications"), list) else []
    )
    normalized["languages"] = (
        normalized["languages"] if isinstance(normalized.get("languages"), list) else []
    )

    if isinstance(normalized["profile"].get("years_of_experience"), str):
        try:
            normalized["profile"]["years_of_experience"] = float(
                normalized["profile"]["years_of_experience"]
            )
        except ValueError:
            normalized["profile"]["years_of_experience"] = 0

    return normalized


def normalize_record(record: dict[str, Any], index: int) -> dict[str, Any]:
    for wrapper_field in JSON_WRAPPER_FIELDS:
        wrapped_value = maybe_parse_json(record.get(wrapper_field))

        if isinstance(wrapped_value, dict):
            return normalize_candidate(wrapped_value, index)

    candidate: dict[str, Any] = {
        "profile": {},
        "career_history": [],
        "education": [],
        "skills": [],
        "redrob_signals": {},
        "certifications": [],
        "languages": [],
    }

    for raw_key, raw_value in record.items():
        if is_blank_value(raw_value):
            continue

        key = str(raw_key).strip()
        value = maybe_parse_json(raw_value)

        if key == "candidate_id":
            candidate["candidate_id"] = str(value)
            continue

        if key in STRUCTURED_FIELDS:
            candidate[key] = value
            continue

        if key in PROFILE_FIELDS:
            candidate["profile"][key] = value
            continue

        if key in REDROB_FIELDS:
            candidate["redrob_signals"][key] = value
            continue

        if "." in key or "[" in key:
            set_nested_value(candidate, key, value)

    return normalize_candidate(candidate, index)


def parse_jsonl_candidates(content: bytes) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []

    for index, line in enumerate(decode_text(content).splitlines(), start=1):
        stripped = line.strip()

        if not stripped:
            continue

        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid JSONL content on line {index}.",
            ) from exc

        if not isinstance(payload, dict):
            raise HTTPException(status_code=400, detail="Each JSONL row must contain one candidate object.")

        candidates.append(normalize_candidate(payload, index))

    return candidates


def parse_json_candidates(content: bytes) -> list[dict[str, Any]]:
    try:
        payload = json.loads(decode_text(content))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="The JSON file is not valid.") from exc

    if isinstance(payload, dict):
        items = payload.get("candidates") if isinstance(payload.get("candidates"), list) else [payload]
    elif isinstance(payload, list):
        items = payload
    else:
        raise HTTPException(status_code=400, detail="The JSON file must contain a candidate object or array.")

    candidates: list[dict[str, Any]] = []

    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise HTTPException(status_code=400, detail="Each JSON candidate must be an object.")

        candidates.append(normalize_candidate(item, index))

    return candidates


def parse_tabular_candidates(content: bytes, extension: str) -> list[dict[str, Any]]:
    buffer = io.BytesIO(content)

    try:
        frame = pd.read_csv(buffer) if extension == ".csv" else pd.read_excel(buffer)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"The {extension[1:].upper()} file could not be parsed.",
        ) from exc

    records = frame.where(pd.notna(frame), None).to_dict(orient="records")
    candidates = [normalize_record(record, index) for index, record in enumerate(records, start=1)]

    return [candidate for candidate in candidates if candidate.get("candidate_id") or candidate.get("profile")]


def parse_uploaded_candidates(filename: str, content: bytes) -> list[dict[str, Any]]:
    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Please upload one of: {supported}.",
        )

    if extension == ".jsonl":
        candidates = parse_jsonl_candidates(content)
    elif extension == ".json":
        candidates = parse_json_candidates(content)
    else:
        candidates = parse_tabular_candidates(content, extension)

    if not candidates:
        raise HTTPException(status_code=400, detail="No candidates were found in the uploaded file.")

    return candidates


def load_candidates_from_server_path(dataset_path: str) -> tuple[list[dict[str, Any]], str]:
    path = Path(dataset_path)

    if not dataset_path.strip():
        raise HTTPException(status_code=400, detail="A dataset path is required for server mode.")

    if not path.is_absolute():
        raise HTTPException(status_code=400, detail="Dataset path must be an absolute path.")

    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=400, detail="Dataset path was not found on this server.")

    try:
        content = path.read_bytes()
    except OSError as exc:
        raise HTTPException(status_code=400, detail="Dataset path could not be read from disk.") from exc

    return parse_uploaded_candidates(path.name, content), str(path)


def extract_job_title(job_description: str) -> str:
    patterns = (
        r"(?:job title|role|position)\s*[:\-]\s*([A-Za-z0-9/&+,\- ]{3,80})",
        r"(?:looking for|hiring|seeking|need(?:ing)?)\s+(?:an?|the)?\s*([A-Za-z0-9/&+,\- ]{3,80}?)(?:\s+(?:with|to|who|for)\b|[.,\n])",
    )

    for pattern in patterns:
        match = re.search(pattern, job_description, flags=re.IGNORECASE)

        if match:
            return re.sub(r"\s+", " ", match.group(1)).strip(" :-")

    first_line = next((line.strip(" :-") for line in job_description.splitlines() if line.strip()), "")

    if first_line and len(first_line.split()) <= 10:
        return first_line

    return "Open Position"


def extract_job_skills(job_description: str) -> tuple[list[str], list[str]]:
    required: list[str] = []
    preferred: list[str] = []
    discovered: list[str] = []

    fragments = re.split(r"[\n\.]", job_description)

    for fragment in fragments:
        lowered = fragment.lower()

        if not lowered.strip():
            continue

        bucket = discovered

        if any(cue in lowered for cue in PREFERRED_CUES):
            bucket = preferred
        elif any(cue in lowered for cue in REQUIRED_CUES):
            bucket = required

        for skill, patterns in SKILL_PATTERNS.items():
            if skill in discovered or skill in required or skill in preferred:
                continue

            if any(re.search(pattern, lowered) for pattern in patterns):
                bucket.append(skill)

    if not required:
        required = (discovered or preferred)[:5]

    if not preferred:
        preferred = [skill for skill in (discovered + preferred) if skill not in required][:3]

    return required, preferred


def build_job_payload(job_description: str) -> dict[str, Any]:
    cleaned_description = job_description.strip()

    if not cleaned_description:
        raise HTTPException(status_code=422, detail="A job description is required.")

    required_skills, preferred_skills = extract_job_skills(cleaned_description)

    return {
        "job_title": extract_job_title(cleaned_description),
        "job_description": cleaned_description,
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
    }


def canonical_skill_lookup(skill_names: list[str]) -> set[str]:
    normalized = normalize_skills(skill_names)

    lookup = {skill.lower().strip() for skill in skill_names if skill}
    lookup.update(item.replace("_", " ") for item in normalized)

    return lookup


def format_education_entries(entries: list[dict[str, Any]]) -> list[str]:
    formatted: list[str] = []

    for entry in entries:
        if not isinstance(entry, dict):
            continue

        details = " ".join(
            str(part).strip()
            for part in (entry.get("degree"), entry.get("field_of_study"))
            if part
        ).strip()
        institution = str(entry.get("institution", "")).strip()
        end_year = entry.get("end_year")
        line = ", ".join(part for part in (details, institution) if part)

        if not line:
            continue

        if end_year:
            line = f"{line} ({end_year})"

        formatted.append(line)

    return formatted


def build_project_highlights(career_history: list[dict[str, Any]]) -> list[str]:
    highlights: list[str] = []

    recent_roles = sorted(
        [role for role in career_history if isinstance(role, dict)],
        key=lambda role: str(role.get("start_date", "")),
        reverse=True,
    )[:3]

    for role in recent_roles:
        title = str(role.get("title", "")).strip()
        company = str(role.get("company", "")).strip()
        description = re.sub(r"\s+", " ", str(role.get("description", "")).strip())
        prefix = " at ".join(part for part in (title, company) if part)

        if description:
            snippet = description[:180].rstrip()

            if len(description) > 180:
                snippet = f"{snippet}..."

            highlights.append(f"{prefix}: {snippet}" if prefix else snippet)
        elif prefix:
            highlights.append(prefix)

    return highlights


def map_matched_skills(skills: list[str], display_order: list[str]) -> list[str]:
    display_map = {skill.lower(): skill for skill in display_order}

    mapped = [display_map.get(skill.lower(), skill) for skill in skills]

    return list(dict.fromkeys(mapped))


def build_candidate_payload(
    source_candidate: dict[str, Any],
    ranked_candidate: dict[str, Any],
    job_payload: dict[str, Any],
) -> dict[str, Any]:
    profile = source_candidate.get("profile", {})
    skill_names = [
        str(skill.get("name", "")).strip()
        for skill in source_candidate.get("skills", [])
        if isinstance(skill, dict) and skill.get("name")
    ]
    skill_lookup = canonical_skill_lookup(skill_names)
    required_skills = job_payload.get("required_skills", [])
    preferred_skills = job_payload.get("preferred_skills", [])
    missing_skills = [
        skill for skill in required_skills if skill.lower().replace("_", " ") not in skill_lookup
    ]

    return {
        "candidate_id": source_candidate.get("candidate_id"),
        "rank": ranked_candidate.get("rank"),
        "candidate_name": profile.get("anonymized_name") or source_candidate.get("candidate_id"),
        "headline": profile.get("headline", ""),
        "current_title": profile.get("current_title", ""),
        "current_company": profile.get("current_company", ""),
        "location": profile.get("location", ""),
        "country": profile.get("country", ""),
        "experience_years": float(profile.get("years_of_experience", 0) or 0),
        "match_score": round(float(ranked_candidate.get("score", 0)) * 100, 1),
        "recommendation": get_recommendation(float(ranked_candidate.get("score", 0) or 0)),
        "skills": skill_names,
        "matched_required_skills": map_matched_skills(
            ranked_candidate.get("matched_required_skills", []),
            required_skills,
        ),
        "matched_preferred_skills": map_matched_skills(
            ranked_candidate.get("matched_preferred_skills", []),
            preferred_skills,
        ),
        "missing_skills": missing_skills,
        "reason": ranked_candidate.get("reasoning", ""),
        "strengths": get_strengths(ranked_candidate),
        "weaknesses": get_weaknesses(ranked_candidate),
        "projects": build_project_highlights(source_candidate.get("career_history", [])),
        "education": format_education_entries(source_candidate.get("education", [])),
        "summary": profile.get("summary", ""),
        "raw_scores": {
            "jd_score": ranked_candidate.get("jd_score"),
            "quality_score": ranked_candidate.get("quality_score"),
            "behavior_score": ranked_candidate.get("behavior_score"),
            "confidence": ranked_candidate.get("confidence"),
        },
    }


@app.get("/")
def home() -> dict[str, str]:
    return {"message": "TalentMind AI Resume Ranker backend is running successfully."}


@app.post("/browse-dataset-path", response_model=None)
def browse_dataset_path() -> Response | dict[str, Any]:
    try:
        import tkinter as tk
        from tkinter import filedialog
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Server-side browse is unavailable in this environment. Paste an absolute path manually.",
        ) from exc

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    try:
        selected_path = filedialog.askopenfilename(
            title="Select candidate dataset",
            filetypes=[
                ("Supported datasets", "*.jsonl *.json *.csv *.xlsx"),
                ("JSONL files", "*.jsonl"),
                ("JSON files", "*.json"),
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx"),
            ],
        )
    finally:
        root.destroy()

    if not selected_path:
        return Response(status_code=204)

    path = Path(selected_path)

    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=400, detail="Selected dataset was not found on disk.")

    return {
        "dataset_path": str(path),
        "size_bytes": path.stat().st_size,
    }


@app.post("/rank")
async def rank(
    job_description: str = Form(...),
    upload_mode: str = Form("file"),
    dataset_path: str | None = Form(None),
    file: UploadFile | None = File(None),
) -> dict[str, Any]:
    if upload_mode == "server":
        candidates, filename = load_candidates_from_server_path(dataset_path or "")
    else:
        if upload_mode != "file":
            raise HTTPException(status_code=400, detail="Unsupported upload mode.")

        if file is None:
            default_csv_path = (Path(__file__).resolve().parent.parent / "sorted_candidates.jsonl").resolve()
            default_jsonl_path = (Path(__file__).resolve().parent.parent / "candidates.jsonl").resolve()

            if is_raw_candidate_csv(default_csv_path):
                candidates, filename = load_candidates_from_server_path(str(default_csv_path))
            elif default_jsonl_path.exists() and default_jsonl_path.is_file():
                candidates, filename = load_candidates_from_server_path(str(default_jsonl_path))
            else:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "No dataset file was provided and the default sorted_candidates.jsonl file is not a valid raw candidate dataset. "
                        "Please upload a raw candidate CSV or provide a JSONL dataset."
                    ),
                )
        else:
            filename = file.filename or "uploaded-dataset"
            content = await file.read()

            if not content:
                raise HTTPException(status_code=400, detail="The uploaded file is empty.")

            candidates = parse_uploaded_candidates(filename, content)

    job_payload = build_job_payload(job_description)

    try:
        from fast_rank import rank_candidates_fast
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="The ranking pipeline could not be loaded. Verify backend dependencies are installed.",
        ) from exc

    try:
        repo_root = Path(__file__).resolve().parent.parent
        ranking_dataset_path = None
        if dataset_path:
            candidate_path = Path(dataset_path)
            if not candidate_path.is_absolute():
                candidate_path = (repo_root / candidate_path).resolve()
            ranking_dataset_path = candidate_path
        else:
            for candidate_name in ("sorted_candidates.jsonl", "sorted_candidtates.jsonl", "candidates.jsonl"):
                candidate_path = repo_root / candidate_name
                if candidate_path.exists() and candidate_path.is_file():
                    ranking_dataset_path = candidate_path
                    break

        ranked_candidates = rank_candidates_fast(
            candidates,
            job_payload,
            dataset_path=ranking_dataset_path,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Candidate ranking failed while processing the uploaded dataset.",
        ) from exc

    candidate_lookup = {candidate["candidate_id"]: candidate for candidate in candidates}
    response_candidates = [
        build_candidate_payload(candidate_lookup[result["candidate_id"]], result, job_payload)
        for result in ranked_candidates
        if result.get("candidate_id") in candidate_lookup
    ]

    return {
        "job": job_payload,
        "summary": {
            "source_file": filename,
            "total_candidates": len(response_candidates),
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        },
        "candidates": response_candidates,
    }
