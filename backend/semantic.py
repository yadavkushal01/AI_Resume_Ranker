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

import numpy as np
from sentence_transformers import SentenceTransformer

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