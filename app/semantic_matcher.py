"""Embedding-based semantic matching for HireMind AI.

The model is loaded lazily so importing the module does not download a model.
"""

from __future__ import annotations

from functools import lru_cache


DEFAULT_MODEL = "all-MiniLM-L6-v2"


@lru_cache(maxsize=2)
def _load_model(model_name: str = DEFAULT_MODEL):
    """Load and cache the sentence-transformer model."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)


def semantic_similarity(
    resume_text: str,
    job_description: str,
    *,
    model_name: str = DEFAULT_MODEL,
) -> float:
    """Return cosine similarity as a percentage in the 0-100 range."""
    if not isinstance(resume_text, str) or not resume_text.strip():
        raise ValueError("resume_text must be a non-empty string.")
    if not isinstance(job_description, str) or not job_description.strip():
        raise ValueError("job_description must be a non-empty string.")

    model = _load_model(model_name)
    embeddings = model.encode(
        [resume_text, job_description],
        normalize_embeddings=True,
    )
    similarity = float(embeddings[0] @ embeddings[1])
    return round(max(0.0, min(1.0, similarity)) * 100, 2)
