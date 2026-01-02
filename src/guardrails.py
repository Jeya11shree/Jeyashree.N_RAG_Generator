import re
from statistics import mean
from typing import List

def sanitize(text: str) -> str:
    if not text: return text
    dangerous_patterns = [
        r"^system:",
        r"^assistant:",
        r"^user:",
        r"^ignore",
        r"^do not follow",
        r"^disregard",
        r"^forget previous",
        r"^new instructions",
    ]
    out = []
    for line in text.splitlines():
        line_lower = line.strip().lower()
        if not any(re.match(pat, line_lower) for pat in dangerous_patterns):
            out.append(line)
    return "\n".join(out)

def meets_evidence_threshold(items: List[dict], threshold: float = 0.2) -> bool:
    if not items: 
        return False
    scores = [i.get("score", 0.0) for i in items]
    avg_score = mean(scores)
    return avg_score >= threshold

def dedupe_chunks(chunks: List[dict]) -> List[dict]:
    seen = set(); unique = []
    for c in chunks:
        text = c.get("text", "")
        key = hash(text)
        if key not in seen:
            seen.add(key)
            unique.append(c)
    return unique

def filter_low_quality_chunks(chunks: List[dict], min_length: int = 50) -> List[dict]:
    return [c for c in chunks if len(c.get("text", "")) >= min_length]
