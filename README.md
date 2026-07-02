# TalentMind AI Resume Ranker

TalentMind AI Resume Ranker is an AI-powered intelligent candidate discovery platform built for the Data & AI Challenge: Intelligent Candidate Discovery. It helps recruiters paste a job description, upload a structured candidate dataset, and receive ranked applicant insights with strengths, weaknesses, skill gaps, and recommendation signals.

## Features

- Recruiter-friendly job description editor with validation and live character counting
- Drag-and-drop dataset upload for `.jsonl`, `.json`, `.csv`, and `.xlsx`
- FastAPI ranking endpoint that accepts multipart form data and supports both uploaded files and server-side dataset paths
- Fast shortlist retrieval that prefers the sorted candidate dataset to reduce ranking time
- Full ranking pipeline with semantic matching, skill matching, career/credibility/behavior signals, and score normalization
- Distinct final ranking values so candidates are easier to compare even when their raw signal scores are similar
- Frontend CSV export for ranked results with `candidate_id`, `rank`, `score`, and `reason`
- Expandable candidate result cards with rank, score, experience, skills, reasoning, projects, education, strengths, weaknesses, and missing skills
- Environment-based API configuration with `VITE_API_URL`
- Responsive React + TypeScript + Tailwind UI optimized for recruiter workflows

## Tech Stack

### Frontend

- React 19
- TypeScript
- Vite
- TanStack Start + TanStack Router
- Tailwind CSS v4
- Radix UI
- Sonner for toast notifications

### Backend

- Python
- FastAPI
- Pandas
- Sentence Transformers
- Scikit-learn
- OpenPyXL

## Project Architecture

- `frontend/` contains the recruiter-facing application, API service layer, UI components, route definitions, hooks, types, utilities, and static assets.
- `backend/` exposes the API surface and wraps the ranking pipeline with fast candidate retrieval, scoring normalization, and ranking export support.
- `backend/fast_retrieval.py` and `backend/fast_rank.py` power the shortlist step before running the full ranking pipeline.
- `backend/scoring.py` now applies normalization so every candidate receives a distinct final score while preserving order.
- `sorted_candidates.jsonl` is preferred when present, and the backend also falls back to `sorted_candidtates.jsonl` or `candidates.jsonl` when needed.

## Folder Structure

```text
AI_Resume_Ranker/
├── backend/
│   ├── main.py
│   ├── ranking.py
│   ├── feature_engineering.py
│   ├── matching.py
│   ├── semantic.py
│   ├── production_analysis.py
│   ├── career_analysis.py
│   ├── behavior.py
│   ├── credibility.py
│   ├── scoring.py
│   └── review_generator.py
├── frontend/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── types/
│   │   └── utils/
│   ├── .env
│   ├── package.json
│   └── vite.config.ts
└── dataset/
```

## Requirements

### Python Setup

- Python 3.11 or newer recommended
- `pip` available in your environment

### Node Setup

- Node.js 22 or newer recommended
- `npm` available in your environment

## Installation

### Backend Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Installation

```bash
cd frontend
npm install
```

## Running the Application

### Running Backend

From the repository root:

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### Running Frontend

```bash
cd frontend
npm run dev
```

The frontend expects the backend at `http://127.0.0.1:8000` by default. Override it in `frontend/.env` when needed.

## Environment Variables

Create or edit `frontend/.env`:

```env
VITE_API_URL=http://127.0.0.1:8000
```

## API Documentation

### Health Check

```http
GET /
```

Example response:

```json
{
  "message": "TalentMind AI Resume Ranker backend is running successfully."
}
```

### Browse Dataset Path

```http
POST /browse-dataset-path
```

Opens a local file picker on the server and returns the selected dataset path when available.

### Rank Candidates

```http
POST /rank
Content-Type: multipart/form-data
```

The backend prefers the sorted dataset file when it is available, applies a fast shortlist retrieval step, and then runs the full scoring pipeline on the shortlisted candidates.

Form fields:

- `job_description`: recruiter-provided job description text
- `upload_mode`: either `file` or `server`
- `dataset_path`: absolute or relative server-side dataset path when `upload_mode=server`
- `file`: uploaded candidate dataset when `upload_mode=file`

Example request with `curl`:

```bash
curl -X POST "http://127.0.0.1:8000/rank" \
  -F "job_description=We are hiring a Retrieval Engineer with Python, vector database, ranking, and LLM experience." \
  -F "upload_mode=file" \
  -F "file=@sorted_candidates.jsonl"
```

Example response shape:

```json
{
  "job": {
    "job_title": "Retrieval Engineer",
    "job_description": "We are hiring a Retrieval Engineer...",
    "required_skills": ["Python", "Retrieval", "Vector Database"],
    "preferred_skills": ["LLM", "Cloud"]
  },
  "summary": {
    "source_file": "sorted_candidates.jsonl",
    "total_candidates": 50,
    "analyzed_at": "2026-07-01T12:00:00+00:00"
  },
  "candidates": [
    {
      "candidate_id": "CAND_0000001",
      "candidate_name": "Candidate 1",
      "match_score": 91.4,
      "reason": "Strong retrieval and semantic alignment"
    }
  ]
}
```

## Dataset Format

### JSONL Format

Each line should contain one candidate object following the challenge schema:

```json
{"candidate_id":"CAND_0000001","profile":{"anonymized_name":"Sample Candidate"},"career_history":[],"education":[],"skills":[],"redrob_signals":{}}
```

### JSON Support

- A top-level array of candidate objects is supported.
- A top-level object with a `candidates` array is supported.

### CSV Support

- CSV files should represent one candidate per row.
- Nested fields such as `profile`, `skills`, `career_history`, `education`, and `redrob_signals` can be supplied as JSON strings.
- Flat column names like `profile.current_title` and `skills[0].name` are also supported.

### XLSX Support

- XLSX files follow the same conventions as CSV.
- Use JSON strings for nested arrays or objects when exporting from spreadsheets.

## Screenshots

- Dashboard screenshot placeholder
- Upload and processing state placeholder
- Ranking results screenshot placeholder

## Future Scope

- Add authentication and recruiter workspaces
- Export ranked reports to PDF and Excel
- Add saved searches and role templates
- Support richer JD parsing with configurable scoring controls
- Add analytics for recruiter decision quality
- Add semantic retrieval tuning and configurable shortlist size

## License

Choose and add the license that matches your hackathon or open-source release strategy.

## Hackathon Information

- Event: Data & AI Challenge
- Theme: Intelligent Candidate Discovery
- Solution: TalentMind AI Resume Ranker

## Authors

- TalentMind project contributors
- Hackathon team members

## Contribution Guide

1. Fork the repository or create a working branch.
2. Keep backend ranking logic isolated unless you are intentionally improving the model pipeline.
3. Run backend and frontend checks before opening a PR.
4. Document dataset assumptions and API changes in the README.

## Acknowledgements

- Data & AI Challenge organizers
- FastAPI, React, TanStack, Tailwind CSS, and open-source AI tooling communities
- The maintainers of Sentence Transformers, Scikit-learn, and Pandas
