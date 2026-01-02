from rank_bm25 import BM25Okapi
from nltk.stem import PorterStemmer
import re

_ps = PorterStemmer()

def _normalize_text(text: str):
    words = re.sub(r'[^\w\s]', '', str(text)).lower().split()
    return ' '.join(_ps.stem(w) for w in words)

def retrieve(query, file_chunks, top_k=5):
    tokenized = [_normalize_text(c['text']).split() for c in file_chunks if c['text'].strip()]
    if not tokenized:
        return []
    bm25 = BM25Okapi(tokenized)
    query_tokens = _normalize_text(query).split()
    scores = bm25.get_scores(query_tokens)
    min_score, max_score = float(min(scores)), float(max(scores))
    norm = [(s-min_score)/(max_score-min_score) if max_score>min_score else 0 for s in scores]
    indices = sorted(range(len(norm)), key=lambda i: norm[i], reverse=True)[:top_k]
    return [
        dict(file_chunks[idx], score=float(norm[idx]))
        for idx in indices if norm[idx] > 0.1
    ]
