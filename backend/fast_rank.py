import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
REPO_ROOT = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

try:
    from fast_retrieval import build_retrieval_index, retrieve_candidates
    from ranking import rank_candidates
except ModuleNotFoundError:
    from backend.fast_retrieval import build_retrieval_index, retrieve_candidates
    from backend.ranking import rank_candidates


def resolve_dataset_path(dataset_path=None) -> Path:
    if dataset_path is None:
        for candidate_name in ("sorted_candidates.jsonl", "sorted_candidtates.jsonl", "candidates.jsonl"):
            path = REPO_ROOT / candidate_name
            if path.exists() and path.is_file():
                return path
        return REPO_ROOT / "candidates.jsonl"

    path = Path(dataset_path)
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    return path


def rank_candidates_fast(candidates, jd, dataset_path=None, index_path=None, top_k=200, cache_path=None, rebuild_cache=False):
    dataset_path = resolve_dataset_path(dataset_path)

    if dataset_path.exists() and dataset_path.is_file():
        if index_path is None:
            index_path = dataset_path.with_suffix(".index.json")

        build_retrieval_index(dataset_path, index_path=index_path)

        job_text = f"{jd.get('job_title', '')} {jd.get('job_description', '')} {' '.join(jd.get('required_skills', []))}"
        retrieved = retrieve_candidates(job_text, dataset_path, index_path=index_path, top_k=top_k)
        shortlisted_candidates = [item.get("candidate") for item in retrieved if item.get("candidate")]

        if shortlisted_candidates:
            return rank_candidates(shortlisted_candidates, jd, cache_path=cache_path, rebuild_cache=rebuild_cache)

    return rank_candidates(candidates, jd, cache_path=cache_path, rebuild_cache=rebuild_cache)
