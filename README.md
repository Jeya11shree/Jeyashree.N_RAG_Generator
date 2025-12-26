```markdown
# rag-multimodal (AI_Intern_Task)

This project is a file-based RAG (Retrieval-Augmented Generation) starter. It ingests multimodal files (text, PDF, images), chunks and indexes their contents, and answers queries by producing structured JSON use-cases / test-cases grounded in retrieved evidence.

## Quick features
- Ingest files from a folder (text, markdown, PDF, DOCX, images via OCR)
- Chunking + deduplication + sanitization (guardrails)
- Hybrid retrieval (TF-IDF + keyword matching) out of the box
- Deterministic generator that returns JSON use-cases grounded in retrieved evidence
- CLI: ingest, index, query (with debug mode showing retrieved chunks)

## Setup (developer)
1. Python 3.10+ recommended
2. Create venv and install:
   ```
   python -m venv .venv
   source .venv/bin/activate   # PowerShell: .venv\\Scripts\\Activate.ps1
   pip install -r requirements.txt
   ```
3. Optional: Tesseract for OCR (if you want image text extraction)
   - Ubuntu: `sudo apt install tesseract-ocr`
   - macOS (brew): `brew install tesseract`
   - Windows: install from the Tesseract site and add to PATH.

4. (Optional) If using OpenAI embeddings or models, set `OPENAI_API_KEY` in your env.

## Files & storage
- sample_data/ - place your sample files here before running `ingest`
- db/chroma/chunks.json - persisted chunk list
- db/chroma/vectorizer.joblib & db/chroma/matrix.joblib - persisted TF-IDF index (if built)
- CLI: src/cli.py drives ingest/index/query

## Usage (CLI)
- Ingest files:
  ```
  python -m src.cli ingest sample_data
  ```
- Build/Load index:
  ```
  python -m src.cli index
  ```
- Query (prints JSON):
  ```
  python -m src.cli query "Create use cases for user signup" --top_k 5 --debug
  ```
  - Use `--debug` to print retrieved chunk scores in logs.

- Save query output to a file:
  ```
  python -m src.cli query "Create use cases for user signup" > result.json
  ```

## How it works (simplified)
1. Ingest: extract text (pdfminer, docx2txt, pytesseract), sanitize, chunk (with overlap), dedupe, and persist chunks.json.
2. Index: build a TF-IDF index (scikit-learn) persisted via joblib.
3. Query: retrieve top_k chunks via hybrid TF-IDF + keyword scoring, check evidence threshold, then generate structured JSON use-cases grounded in evidence.

## Notes & next steps
- For better semantic retrieval, swap TF-IDF for embeddings + vector DB (Chroma / FAISS) — supports paraphrase queries.
- If you add LLM generation: always instruct the model to use ONLY retrieved evidence and cite sources; implement evidence-threshold checks.
- Add sample_data files (PRD, API spec, UI screenshot pdf/png) to test end-to-end.

## Contact / Demo
- Demo video link: see demo_recording_link.txt
```