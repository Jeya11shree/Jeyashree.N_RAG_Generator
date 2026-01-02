import os
from pathlib import Path
from typing import List, Dict
from chunking import chunk_text_smart

def extract_text_from_txt_md(file_path):
    try:
        return Path(file_path).read_text(encoding="utf-8")
    except Exception as e:
        print(f"[TXT/MD] Error {file_path}: {e}")
        return ""

def extract_text_from_docx(file_path):
    try:
        import docx
        doc = docx.Document(str(file_path))
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        print(f"[DOCX] Error {file_path}: {e}")
        return ""

def extract_text_from_pdf(file_path):
    try:
        import pdfplumber
        text = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t: text.append(t)
        return "\n".join(text)
    except Exception as e:
        print(f"[PDF] Error {file_path}: {e}")
        return ""

def extract_text_from_image(file_path):
    try:
        from PIL import Image
        import pytesseract
        return pytesseract.image_to_string(Image.open(file_path))
    except Exception as e:
        print(f"[IMAGE/OCR] Error {file_path}: {e}")
        return ""

def file_to_chunks(file_path: Path) -> List[Dict]:
    ext = file_path.suffix.lower()
    content = ""
    if ext in [".txt", ".md"]:
        content = extract_text_from_txt_md(file_path)
    elif ext == ".pdf":
        content = extract_text_from_pdf(file_path)
    elif ext == ".docx":
        content = extract_text_from_docx(file_path)
    elif ext in [".png", ".jpg", ".jpeg"]:
        content = extract_text_from_image(file_path)
    if not content:
        return []
    chunks = chunk_text_smart(content)
    return [{
        "text": c,
        "source": file_path.name,
        "chunk_id": idx,
        "char_count": len(c),
        "word_count": len(c.split()),
    } for idx, c in enumerate(chunks) if c.strip()]

def ingest_files(files: List[Path]):
    all_chunks = []
    for file in files:
        all_chunks += file_to_chunks(file)
    return all_chunks


if __name__ == "__main__":
    import sys, json
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("sample_docs")
    chunks = ingest_files(list(folder.glob("*")))
    with open("data/index.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"[Ingest] {folder} processed.")