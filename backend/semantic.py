# ==========================================================
# semantic.py
# ==========================================================

"""
Semantic Matching Module

Responsibilities
----------------
1. Load SentenceTransformer model
2. Generate embeddings
3. Compute cosine similarity
4. Provide reusable embedding utilities
"""

import hashlib
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

try:
    import faiss
except ImportError:  # pragma: no cover
    faiss = None

from feature_engineering import (
    build_candidate_text,
    build_jd_text
)


# ==========================================================
# Load Embedding Model
# ==========================================================

MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


# ==========================================================
# Embedding Generation
# ==========================================================

def generate_embedding(text):
    """
    Generate embedding for a text.

    Parameters
    ----------
    text : str

    Returns
    -------
    numpy.ndarray
    """

    if not text:
        text = ""

    embedding = model.encode(
        text,
        convert_to_numpy=True
    )

    return embedding


def generate_embeddings(texts, batch_size=64):
    """
    Generate embeddings for a list of texts in batches.

    Parameters
    ----------
    texts : list[str]
    batch_size : int

    Returns
    -------
    numpy.ndarray
    """

    if not texts:
        return np.empty((0, 0), dtype=float)

    normalized = [text if text else "" for text in texts]

    embeddings = model.encode(
        normalized,
        batch_size=batch_size,
        convert_to_numpy=True,
    )

    return embeddings


# ==========================================================
# FAISS Helpers
# ==========================================================


def normalize_embeddings(embeddings):
    embeddings = np.asarray(embeddings, dtype=np.float32)

    if embeddings.ndim == 1:
        embeddings = embeddings.reshape(1, -1)

    if embeddings.size == 0:
        return embeddings

    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1.0

    return embeddings / norms


def build_faiss_index(embeddings, use_cosine=True):
    if faiss is None:
        raise RuntimeError(
            "faiss is not installed. Install with 'pip install faiss-cpu'."
        )

    embeddings = np.asarray(embeddings, dtype=np.float32)

    if embeddings.size == 0:
        return None

    dim = embeddings.shape[1]

    if use_cosine:
        embeddings = normalize_embeddings(embeddings)
        index = faiss.IndexFlatIP(dim)
    else:
        index = faiss.IndexFlatL2(dim)

    index.add(embeddings)
    return index


def search_faiss_index(index, queries, top_k=1, normalize=True):
    queries = np.asarray(queries, dtype=np.float32)

    if queries.ndim == 1:
        queries = queries.reshape(1, -1)

    if normalize:
        queries = normalize_embeddings(queries)

    if index is None or index.ntotal == 0:
        shape = (queries.shape[0], 0)
        return np.empty(shape, dtype=np.float32), np.empty(shape, dtype=np.int64)

    distances, indices = index.search(queries, top_k)
    return distances, indices


def calculate_semantic_scores_with_faiss(candidate_embeddings, jd_embedding):
    if len(candidate_embeddings) == 0:
        return []

    candidate_embeddings = np.asarray(candidate_embeddings, dtype=np.float32)
    jd_embedding = np.asarray(jd_embedding, dtype=np.float32).reshape(1, -1)

    if faiss is None:
        return [
            calculate_semantic_match(
                candidate_embedding,
                jd_embedding[0]
            )["semantic_score"]
            for candidate_embedding in candidate_embeddings
        ]

    candidate_embeddings = normalize_embeddings(candidate_embeddings)
    query_embedding = normalize_embeddings(jd_embedding)
    index = build_faiss_index(candidate_embeddings, use_cosine=True)

    top_k = candidate_embeddings.shape[0]
    distances, indices = search_faiss_index(
        index,
        query_embedding,
        top_k=top_k,
        normalize=False
    )

    scores = np.zeros(top_k, dtype=float)
    scores[indices[0]] = distances[0]

    return scores.tolist()


# ==========================================================
# Candidate Embedding Cache
# ==========================================================


def build_candidate_text_hash(candidate_texts):
    digest = hashlib.sha256()

    for text in candidate_texts:
        digest.update((text or "").encode("utf-8", errors="ignore"))
        digest.update(b"\n")

    return digest.hexdigest()


def load_cached_candidate_embeddings(cache_path, candidate_ids, candidate_text_hash):
    cache_path = Path(cache_path)

    if not cache_path.exists():
        return None

    try:
        with np.load(cache_path, allow_pickle=True) as data:
            cached_ids = data["candidate_ids"].tolist()
            cached_hash = data["candidate_text_hash"].tolist()

            if cached_ids == list(candidate_ids) and cached_hash == candidate_text_hash:
                return data["embeddings"]
    except Exception:
        return None

    return None


def save_cached_candidate_embeddings(cache_path, candidate_ids, candidate_text_hash, embeddings):
    cache_path = Path(cache_path)
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    np.savez_compressed(
        cache_path,
        candidate_ids=np.array(candidate_ids, dtype="U"),
        candidate_text_hash=np.array([candidate_text_hash], dtype="U"),
        embeddings=np.asarray(embeddings, dtype=np.float32),
    )


def get_cached_candidate_embeddings(candidates, cache_path=None, rebuild_cache=False):
    candidate_ids = [
        candidate.get("candidate_id", "")
        for candidate in candidates
    ]

    candidate_texts = [
        build_candidate_text(candidate)
        for candidate in candidates
    ]

    candidate_text_hash = build_candidate_text_hash(
        candidate_texts
    )

    if cache_path is None:
        cache_path = Path(__file__).resolve().parent / "candidate_embeddings.npz"

    if not rebuild_cache:
        embeddings = load_cached_candidate_embeddings(
            cache_path,
            candidate_ids,
            candidate_text_hash,
        )

        if embeddings is not None:
            return embeddings

    embeddings = generate_embeddings(candidate_texts)

    save_cached_candidate_embeddings(
        cache_path,
        candidate_ids,
        candidate_text_hash,
        embeddings,
    )

    return embeddings


# ==========================================================
# Candidate Embedding
# ==========================================================

def build_candidate_embedding(candidate):
    """
    Convert candidate profile into embedding.
    """

    candidate_text = build_candidate_text(candidate)

    return generate_embedding(candidate_text)


# ==========================================================
# JD Embedding
# ==========================================================

def build_jd_embedding(jd):
    """
    Convert Job Description into embedding.
    """

    jd_text = build_jd_text(jd)

    return generate_embedding(jd_text)


# ==========================================================
# Semantic Similarity
# ==========================================================

def calculate_semantic_match(
    candidate_embedding,
    jd_embedding
):
    """
    Cosine similarity between candidate and JD.

    Returns
    -------
    float
        Range: 0-1
    """

    candidate_norm = np.linalg.norm(candidate_embedding)
    jd_norm = np.linalg.norm(jd_embedding)

    if candidate_norm == 0 or jd_norm == 0:
        similarity = 0.0
    else:
        similarity = float(np.dot(candidate_embedding, jd_embedding) / (candidate_norm * jd_norm))

    return {
        "semantic_score" : float(similarity)
    }

# ==========================================================
# Complete Semantic Pipeline
# ==========================================================

def calculate_semantic_features(
    candidate,
    jd_embedding
):
    """
    Complete semantic matching pipeline.

    Returns
    -------
    dict
    """

    candidate_embedding = build_candidate_embedding(
        candidate
    )

    semantic_score = calculate_semantic_match(

        candidate_embedding,

        jd_embedding

    )

    return {

        "semantic_score": round(
            semantic_score,
            4
        )

    }


# ==========================================================
# Batch Candidate Embeddings (Optional)
# ==========================================================

def build_candidate_embeddings(candidates):
    """
    Precompute embeddings for all candidates.

    Useful when ranking thousands of candidates.
    """

    embeddings = {}

    for candidate in candidates:

        candidate_id = candidate.get(
            "candidate_id",
            ""
        )

        embeddings[candidate_id] = build_candidate_embedding(
            candidate
        )

    return embeddings


# ==========================================================
# Batch Semantic Matching (Optional)
# ==========================================================

def calculate_batch_semantic_scores(
    candidates,
    jd_embedding
):
    """
    Compute semantic similarity for all candidates.

    Returns
    -------
    dict

    {
        candidate_id: semantic_score
    }
    """

    scores = {}

    embeddings = build_candidate_embeddings(
        candidates
    )

    for candidate in candidates:

        candidate_id = candidate.get(
            "candidate_id",
            ""
        )

        score = calculate_semantic_match(

            embeddings[candidate_id],

            jd_embedding

        )

        scores[candidate_id] = round(
            score,
            4
        )

    return scores