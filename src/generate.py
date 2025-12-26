"""Generate structured JSON use-cases / test-cases grounded in retrieved evidence.

Includes a small extractor to find "course name" from OCR/text evidence for targeted queries.
"""
import logging
from typing import List, Optional
import re

logger = logging.getLogger(__name__)

KEYWORD_MAP = {
    "email": "email",
    "password": "password",
    "verify": "verification",
    "verification": "verification",
    "redirect": "redirect",
    "captcha": "captcha",
    "rate": "rate_limit",
    "throttle": "rate_limit",
}


def _detect_features(evidence: List[dict]):
    text = " \n ".join([e.get("text", "") for e in evidence]) if evidence else ""
    textl = text.lower()
    feats = set()
    for k in KEYWORD_MAP:
        if k in textl:
            feats.add(KEYWORD_MAP[k])
    return feats


def extract_course_name_from_evidence(evidence: List[dict]) -> Optional[str]:
    """Heuristic extractor: look for course name lines or Degree/Branch fields.

    Returns a single best candidate string or None.
    """
    if not evidence:
        return None

    # Patterns likely to contain degree/branch or course name
    patterns = [
        r"Degree\s*/\s*Branch\s*[:\-]\s*(.+)",        # "Degree / Branch: M.Sc..."
        r"Degree\s*[:\-]\s*(.+)",
        r"Course\s*Name\s*[:\-]\s*(.+)",
        r"Course\s*Name\s*(.+)",
        r"Degree\s*\/\s*Branch\s*(.+)",
    ]

    for e in evidence:
        text = e.get("text", "")
        if not text:
            continue
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                val = m.group(1).strip()
                val = val.splitlines()[0]
                val = re.sub(r"[ \t\r\n]+$", "", val)
                if val:
                    return val

        # fallback: look for uppercase-ish table lines (course names are often uppercase)
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        for ln in lines:
            words = ln.split()
            if len(words) >= 2:
                alpha = sum(1 for ch in ln if ch.isalpha())
                upper = sum(1 for ch in ln if ch.isupper())
                if alpha > 0 and (upper / alpha) > 0.5 and len(ln) < 160:
                    return ln
    return None


def _make_use_case(title, steps, expected, preconditions=None, test_data=None, negative=None, boundary=None, citations=None):
    return {
        "title": title,
        "goal": title,
        "preconditions": preconditions or [],
        "test_data": test_data or {},
        "steps": steps,
        "expected_results": expected,
        "negative_cases": negative or [],
        "boundary_cases": boundary or [],
        "citations": citations or [],
    }


def generate_use_cases(query: str, evidence: List[dict], top_k: int = 5, evidence_threshold: float = 0.05):
    """Generate a list of use-cases (JSON) grounded in evidence.

    Special-case: if query asks for "course name" attempt to extract the field and return it.
    """
    avg_score = 0.0
    if evidence:
        avg_score = sum(e.get("score", 0.0) for e in evidence) / len(evidence)

    out = {"query": query, "avg_evidence_score": avg_score, "use_cases": []}

    # If the user asks explicitly about course name, attempt extraction first
    qlow = query.lower()
    if "course name" in qlow or ("what" in qlow and "course" in qlow):
        course = extract_course_name_from_evidence(evidence)
        citations = [{"id": e.get("id"), "source": e.get("source"), "score": e.get("score")} for e in (evidence[:top_k] if evidence else [])]
        if course:
            return {"query": query, "course_name": course, "evidence": citations}
        # else continue to normal clarification logic

    if avg_score < evidence_threshold:
        out["clarify"] = True
        out["message"] = "Insufficient high-confidence evidence to fully ground answers. Please provide more documents or confirm I should proceed with assumptions."
        out["assumptions"] = ["Standard signup flow with email + password", "Email verification is supported"]
        out["evidence"] = evidence
        return out

    feats = _detect_features(evidence)
    citations = [{"id": e.get("id"), "source": e.get("source"), "score": e.get("score")} for e in (evidence[:top_k] if evidence else [])]

    # Basic success flow use-case examples
    steps = ["Open the Signup page.", "Enter a valid email.", "Enter a valid password.", "Submit the form."]
    expected = ["Account is created successfully.", "User is redirected or shown next steps per product spec."]
    uc = _make_use_case(
        "Signup with valid email and password",
        steps,
        expected,
        preconditions=["User is logged out"],
        test_data={"email": "new_user@example.com", "password": "StrongPass#123"},
        citations=citations,
    )
    out["use_cases"].append(uc)

    # Duplicate email use-case
    steps = ["Open Signup page.", "Enter an existing email.", "Enter a valid password.", "Submit the form."]
    expected = ["Error shown (e.g., 'Email already exists').", "No new account is created."]
    uc2 = _make_use_case(
        "Reject duplicate email signup",
        steps,
        expected,
        preconditions=["An account exists for existing@example.com"],
        test_data={"email": "existing@example.com", "password": "AnotherStrong#1"},
        citations=citations,
    )
    out["use_cases"].append(uc2)

    # Password policy use-case
    if "password" in feats:
        steps = ["Open Signup page.", "Enter valid email.", "Enter a weak password (e.g., '12345').", "Submit the form."]
        expected = ["Inline validation explaining password rules.", "Signup is blocked until password meets policy."]
        uc3 = _make_use_case("Password policy validation", steps, expected, test_data={"password": "12345"}, citations=citations)
        out["use_cases"].append(uc3)

    # Email verification use-case
    if "verification" in feats:
        steps = ["Complete signup and receive verification email.", "Open verification link."]
        expected = ["Account is verified if token valid.", "If token invalid or expired appropriate error is shown and resend flow recommended."]
        uc4 = _make_use_case(
            "Email verification flows", steps, expected, preconditions=["User signed up and received an email"], citations=citations
        )
        out["use_cases"].append(uc4)

    # Rate limit / throttle use-case
    if "rate_limit" in feats:
        steps = ["Trigger resend verification repeatedly (e.g., 5 times within 1 minute)."]
        expected = ["Throttling applied or clear feedback to user about resend limits."]
        uc5 = _make_use_case("Resend verification throttling", steps, expected, citations=citations)
        out["use_cases"].append(uc5)

    out["evidence"] = citations
    return out