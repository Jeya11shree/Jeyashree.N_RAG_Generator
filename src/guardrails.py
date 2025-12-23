"""Simple guardrails: sanitization, evidence checks, dedupe helpers."""

import re


def sanitize(text: str) -> str:
    """Strip obvious prompt-injection markers and long instruction headers.

    This is intentionally conservative: it removes lines that look like system
    messages or assistant instructions embedded inside documents.
    """
    if not text:
        return text
    lines = []
    for L in text.splitlines():
        if re.match(r"^(system:|assistant:|user:|do not follow|ignore).*", L.strip().lower()):
            continue
        lines.append(L)
    return "\n".join(lines)


def meets_evidence_threshold(items, threshold: float = 0.2) -> bool:
    """Return True if average evidence score meets the threshold."""
    if not items:
        return False
    avg = sum(i.get("score", 0.0) for i in items) / len(items)
    return avg >= threshold


def dedupe_chunks(chunks):
    seen = set()
    out = []
    for c in chunks:
        h = hash(c.get("text", ""))
        if h in seen:
            continue
        seen.add(h)
        out.append(c)
    return out
