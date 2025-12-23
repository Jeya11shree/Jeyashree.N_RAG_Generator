"""Hybrid retrieval: TF-IDF vector + lightweight keyword matching.

This module loads chunks persisted by `ingest.run()` and builds a simple
TF-IDF vector index (scikit-learn) stored in-memory for retrieval.

Retrieval returns a list of evidence items with `score` and `source`.
"""

import json
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

CHUNKS_PATH = Path("db/chroma/chunks.json")
VECT_PKL = Path("db/chroma/vectorizer.joblib")
MAT_PKL = Path("db/chroma/matrix.joblib")
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import joblib
except Exception:
    TfidfVectorizer = None
    cosine_similarity = None
    joblib = None


def _load_chunks():
    if not CHUNKS_PATH.exists():
        return []
    return json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))


def _build_index(chunks):
    texts = [c["text"] for c in chunks]
    if not TfidfVectorizer:
        return None, None
    vec = TfidfVectorizer(max_features=20000)
    mat = vec.fit_transform(texts)
    # persist if joblib available
    try:
        if joblib:
            VECT_PKL.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(vec, VECT_PKL)
            joblib.dump(mat, MAT_PKL)
    except Exception:
        pass
    return vec, mat


def run_build_index():
    chunks = _load_chunks()
    # try loading persisted index
    if joblib and VECT_PKL.exists() and MAT_PKL.exists():
        try:
            vec = joblib.load(VECT_PKL)
            mat = joblib.load(MAT_PKL)
            return vec, mat, chunks
        except Exception:
            pass

    vec, mat = _build_index(chunks)
    return vec, mat, chunks


def _keyword_score(text: str, query: str) -> float:
    qtokens = set(query.lower().split())
    tokens = set(text.lower().split())
    if not qtokens:
        return 0.0
    return len(qtokens & tokens) / len(qtokens)


def retrieve(query: str, top_k: int = 5, alpha: float = 0.8) -> List[dict]:
    """Return top_k evidence chunks with combined vector+keyword score.

    alpha weights vector score (0..1). If TF-IDF is unavailable alpha is ignored.
    """
    chunks = _load_chunks()
    if not chunks:
        return []

    vec, mat = _build_index(chunks)
    keyword_scores = [_keyword_score(c["text"], query) for c in chunks]

    vec_scores = [0.0] * len(chunks)
    if vec is not None and cosine_similarity is not None:
        qv = vec.transform([query])
        sims = cosine_similarity(qv, mat).flatten()
        vec_scores = [float(s) for s in sims]

    results = []
    for i, c in enumerate(chunks):
        v = vec_scores[i]
        k = keyword_scores[i]
        score = alpha * v + (1 - alpha) * k if vec is not None else k
        results.append({"id": c["id"], "source": c.get("source"), "text": c["text"], "score": float(score)})

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


def show_retrieved(query: str, top_k: int = 5):
    res = retrieve(query, top_k=top_k)
    for r in res:
        logger.info("score=%.3f source=%s", r["score"], r["source"])
    return res
