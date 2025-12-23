"""Ingestion: file discovery, parsing, chunking and local index persistence.

This module keeps everything file-based: extracted chunks are persisted to
`db/chroma/chunks.json` and a small TF-IDF index is persisted to
`db/chroma/vectorizer.pkl` and `db/chroma/vectors.npy` for retrieval.

The extractor supports plain text/markdown, YAML, PDF and images (OCR).
"""

import os
import json
import logging
from pathlib import Path
import hashlib
from . import guardrails

logger = logging.getLogger(__name__)

try:
    from pdfminer.high_level import extract_text as pdf_extract
except Exception:
    pdf_extract = None

try:
    from PIL import Image
    import pytesseract
except Exception:
    Image = None
    pytesseract = None

CHUNKS_PATH = Path("db/chroma/chunks.json")
IDX_DIR = Path("db/chroma")
IDX_DIR.mkdir(parents=True, exist_ok=True)


def _read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def extract_text(path: str) -> str:
    p = Path(path)
    ext = p.suffix.lower()
    try:
        if ext in [".md", ".txt", ".yaml", ".yml"]:
            return _read_text_file(p)
        if ext == ".pdf" and pdf_extract:
            return pdf_extract(str(p)) or ""
        if ext in [".png", ".jpg", ".jpeg"] and Image and pytesseract:
            img = Image.open(p)
            return pytesseract.image_to_string(img) or ""
        if ext == ".docx":
            try:
                import docx2txt

                return docx2txt.process(str(p)) or ""
            except Exception:
                return ""
    except Exception as e:
        logger.warning("Failed extract from %s: %s", path, e)
    return ""


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100):
    if not text:
        return []
    text = text.replace("\r\n", "\n").strip()
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i : i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks


def _id_for(source: str, idx: int) -> str:
    h = hashlib.sha1(f"{source}:{idx}".encode()).hexdigest()
    return h


def run(input_path: str = "sample_data", persist: bool = True):
    """Discover files under `input_path`, extract and chunk them, and persist.

    Returns list of chunk dicts: {id, source, text, meta}
    """
    base = Path(input_path)
    files = list(base.rglob("*.*"))
    all_chunks = []
    for f in files:
        text = extract_text(str(f))
        text = (text or "").strip()
        if not text:
            continue
        # sanitize to remove embedded instructions that could be prompt-injection
        text = guardrails.sanitize(text)
        if not text:
            continue
        chunks = chunk_text(text)
        for idx, c in enumerate(chunks):
            chunk = {
                "id": _id_for(str(f), idx),
                "source": str(f.relative_to(Path.cwd())) if f.is_relative_to(Path.cwd()) else str(f),
                "text": c,
                "meta": {"filename": f.name, "index": idx},
            }
            all_chunks.append(chunk)

    # dedupe before persisting
    all_chunks = guardrails.dedupe_chunks(all_chunks)
    if persist:
        CHUNKS_PATH.parent.mkdir(parents=True, exist_ok=True)
        CHUNKS_PATH.write_text(json.dumps(all_chunks, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info("Persisted %d chunks to %s", len(all_chunks), CHUNKS_PATH)

    return all_chunks


def load_chunks():
    if not CHUNKS_PATH.exists():
        return []
    return json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))
