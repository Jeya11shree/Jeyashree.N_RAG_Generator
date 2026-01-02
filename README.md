# File-Based Multimodal RAG Test-Case Generator

## Overview

This project is a Retrieval-Augmented Generation (RAG) system that generates **structured JSON test cases/use cases** grounded strictly in context from any uploaded files—including DOCX, PDF, Markdown, and images (PNG/JPG with OCR).  
It’s designed for QA and product teams to create robust, evidence-based test coverage from requirements and UI artifacts.
I have used Python 3.12 version for this entire project.

---

## Features

- **Multimodal ingestion:** PDFs, DOCX, Markdown, PNG/JPG screenshots
- **OCR** extracts content from images for full evidence coverage
- **Chunking and hybrid (vector+keyword) retrieval** for best match
- **Strict JSON output** with test-case fields:
  `Use Case Title, Goal, Preconditions, Test Data, Steps, Expected Results, Negative cases, Boundary cases`
- **Guardrails:** Reduces hallucination, returns `"insufficient_evidence"` if answer can’t be grounded
- **Debug & observability:** Evidence/source tracing available in debug mode
- **Clean modular design** for easy extension

---

## Project Structure & File Guide

| File/Folder                | Purpose                                                                                 |
|----------------------------|-----------------------------------------------------------------------------------------|
| `README.md`                | Project guide, setup, usage, and file explanations (this doc!)                          |
| `.env`                     | **Your API key config. You must edit to add your own GROQ_API_KEY before running.**     |
| `requirements.txt`         | All Python dependencies, pip-installable; generated from project environment            |
| `Dockerfile`               | (Optional) For containerized deployment                                                 |
| `src/`                     | All main Python source code modules                                                     |
| ├── `ingestion.py`         | File reading, type-detection, OCR/image parsing, chunking logic                         |
| ├── `retrieval.py`         | Chunk search: keyword, vector, or hybrid retrieval                                      |
| ├── `generation.py`        | Uses LLM (GROQ) to generate test-case JSON, guarded by retrieved context                |
| ├── `ocr_utils.py`         | Helpers for image to text (OCR)                                                         |
| ├── `guards.py`            | Hallucination guardrails, minimum evidence threshold logic                              |
| └── `streamlit_app.py`     | Main Streamlit UI app                                                                   |
                                                            
| `data/sample/`             | **Sample input files** (PDF, DOCX, PNG/JPG). Used to demo the upload and ingestion.     |
| `logs/`                    | Logs for debug/tracing. Non-essential, safe to ignore/clear                             |
| `docs/`                    | (Optional) Design diagrams, extra notes, architecture images                            |
| `tests/`                   | Very basic test cases, e.g. for ingestion, retrieval, generation sanity checks          |

**IMPORTANT:**  
- Before running, you must edit `.env` and paste your Groq API key.  

## Setup & Usage

### 1. Clone the repo

```bash
git clone https://github.com/<your-username>/file-rag-testcase-gen.git
cd file-rag-testcase-gen
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

- Open the included `.env` file.
- Paste your **GROQ_API_KEY** (required to access the language model):

```
GROQ_API_KEY=YOUR_GROQ_API_KEY
```

### 4. Run the app

- **CLI:**
  ```bash
  python run.py
  ```
- **Or Web UI (recommended for upload/testing):**
  ```bash
  streamlit run src\streamlit_app.py
  ```

---

## Example Usage

- Add sample PDFs/DOCXs/PNGs (see `data/sample/`) or upload your own via the UI.
- Enter a query into the UI, e.g.: Generate test cases for "Twin beds" and "Double bed" filters in hotel search and there is also a folder inside ('data/sample/queries') which contains a set of questions in text files related to the sample data given.
- Get a clear, assignment-format JSON with evidence. Download as needed.
- If the context is missing, you’ll get an `"insufficient_evidence"` message or prompt for more info.

---

## Architecture and Design

**Flow:**  
*Ingestion → OCR (if image) → Chunking → Embedding & keyword indexing → Hybrid retrieval → LLM generation (guarded by evidence) → JSON output.*

- Each module is separated for clarity and easy future improvements.
- UI is makes demo/upload/testing much easier.

---


## Sample Dataset

- `data/sample/` has a few representative files for your quick testing and recruiter demo.

---

## Walkthrough Video

- [Demo Video (Drive)] Link: https://drive.google.com/file/d/1eZhbAMxAD9PVh3o5s5tCStT7frE5R9F5/view?usp=drive_link

---

## Testing & Debug

- To run minimal tests, check the `/tests` directory.
- Enable debug mode in UI to see chunk evidence and scores.

---

## Contributor

- Jeyashree N [LinkedIn/email] : https://www.linkedin.com/in/jeyashree-n/ and jeyashreeceg@gmail.com
- Assignment reviewers: santhosh@devassure.io, divya@devassure.io

---
