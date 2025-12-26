# contents of file
from pathlib import Path
import sys
import os
import shutil
import json
from typing import List

# Ensure project root is on sys.path so "from src import ..." works
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

# Import project modules (existing)
from src import ingest, retrieval, generate, guardrails, utils

# Constants
UPLOAD_DIR = Path("sample_data_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Page config
st.set_page_config(page_title="RAG Multimodal Demo", layout="wide", page_icon="🧠")

# -- Custom styling (gradient header, cards, buttons) --
CSS = """
/* Gradient header */
.header {
  background: linear-gradient(90deg, #3a7bd5 0%, #00d2ff 100%);
  color: white;
  padding: 18px 24px;
  border-radius: 8px;
  margin-bottom: 20px;
}
.header h1 {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 0.4px;
}

/* Card for retrieved chunks */
.rag-card {
  background: white;
  border-radius: 10px;
  padding: 14px;
  box-shadow: 0 6px 18px rgba(32,33,36,0.08);
  margin-bottom: 12px;
  border-left: 6px solid #00d2ff;
}
.rag-card small {
  color: #6b7280;
}
.badge {
  display:inline-block;
  padding:4px 8px;
  border-radius:12px;
  font-size:12px;
  color:#fff;
  background: #2563eb;
  margin-right:8px;
}

/* Buttons */
.stButton>button {
  background: linear-gradient(90deg,#06b6d4,#3b82f6);
  color: white;
  border: none;
}

/* Sidebar tweaks */
[data-testid="stSidebar"] .css-1d391kg {
  background: linear-gradient(180deg,#f8fafc,#eff6ff);
}

/* JSON area */
.stJson {
  background: #0f172a;
  color: #e6eef8;
  padding: 10px;
  border-radius: 8px;
}
"""

st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

# Header
st.markdown(
    """
    <div class="header">
      <h1>RAG Multimodal — Use-case / Test-case Generator</h1>
      <div style="font-size:13px; margin-top:6px;">Upload docs (md, pdf, docx, png/jpg), ingest, and generate structured JSON test-cases grounded in evidence.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Helper functions
def save_uploaded_files(uploaded_files: List[st.runtime.uploaded_file_manager.UploadedFileManager], target_dir: Path):
    target_dir.mkdir(parents=True, exist_ok=True)
    saved_paths = []
    for up in uploaded_files:
        dest = target_dir / up.name
        with open(dest, "wb") as f:
            f.write(up.getbuffer())
        saved_paths.append(dest)
    return saved_paths

def list_uploaded_files(target_dir: Path):
    return sorted([p for p in target_dir.iterdir() if p.is_file()])

def clear_uploads(target_dir: Path):
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir()

# Layout
col_left, col_right = st.columns([1, 2], gap="large")

with col_left:
    st.subheader("Upload & Ingest")
    uploaded = st.file_uploader("Choose files (md, txt, pdf, docx, png/jpg)", accept_multiple_files=True)
    if uploaded:
        if st.button("Save & Ingest uploaded files"):
            with st.spinner("Saving files and running ingestion..."):
                saved = save_uploaded_files(uploaded, UPLOAD_DIR)
                chunks = ingest.run(input_path=str(UPLOAD_DIR), persist=True)
            st.success(f"Ingested {len(chunks)} chunks from {len(saved)} files.")
            st.info("Tip: Use 'Build / Load index' before querying.")

    if st.button("Clear uploaded files"):
        clear_uploads(UPLOAD_DIR)
        st.success("Cleared upload directory.")

    st.markdown("**Uploaded files**")
    files = list_uploaded_files(UPLOAD_DIR)
    if files:
        for f in files:
            st.write(f"- {f.name} ({f.stat().st_size} bytes)")
    else:
        st.write("No uploaded files. Upload sample files to start.")

    st.markdown("---")
    st.subheader("Indexing")
    if st.button("Build / Load TF-IDF index (local)"):
        with st.spinner("Building/Loading index..."):
            vec, mat, chunks = retrieval.run_build_index()
        st.success(f"Index ready. {len(chunks)} chunks available.")
        st.write("You can now query the knowledge base.")

with col_right:
    st.subheader("Query & Generate")
    q = st.text_input("Enter your query", value="Create use cases for user signup")
    top_k = st.slider("Top K (retrieved chunks)", 1, 10, 5)
    evidence_threshold = st.number_input("Evidence threshold (0..1)", min_value=0.0, max_value=1.0, value=0.2, step=0.01)
    debug = st.checkbox("Show retrieved chunks (debug)", value=True)

    if st.button("Run Query and Generate JSON"):
        if not q.strip():
            st.error("Please provide a non-empty query.")
        else:
            # Ensure index is available
            with st.spinner("Retrieving evidence..."):
                _vec, _mat, _chunks = retrieval.run_build_index()
                retrieved = retrieval.retrieve(q, top_k=top_k)

            if not retrieved:
                st.warning("No evidence was retrieved. Try ingesting more documents.")
            # Debug view: cards with nice styling
            if debug and retrieved:
                st.markdown("### Retrieved evidence (top_k)", unsafe_allow_html=True)
                for r in retrieved:
                    snippet = (r.get("text") or "")[:400]
                    card_html = f"""
                    <div class="rag-card">
                      <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div><span class="badge">score: {r.get('score'):.3f}</span> <small>{r.get('source') or 'unknown'}</small></div>
                      </div>
                      <div style="margin-top:8px; color:#111827;">{snippet.replace(chr(10), '<br/>')}</div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)

            # Evidence threshold check
            if not guardrails.meets_evidence_threshold(retrieved, threshold=evidence_threshold):
                st.warning("Average evidence score below threshold. Ask for more documents or reduce threshold.")
                st.json({"clarify": True, "message": "Insufficient evidence; provide more documents or confirm assumptions.", "evidence": retrieved})
            else:
                with st.spinner("Generating use-cases..."):
                    out = generate.generate_use_cases(q, retrieved, top_k=top_k, evidence_threshold=evidence_threshold)
                st.markdown("### Generated JSON output")
                st.json(out)

                # Download button with styled wrapper
                result_json = json.dumps(out, indent=2)
                st.download_button(label="⬇️ Download JSON", data=result_json, file_name="use_cases.json", mime="application/json")

    st.markdown("---")
    st.markdown(
        """
        **Usage tips**  
        - Upload PRD, API specs, and screenshots.  
        - Use Debug mode to inspect retrieved chunks and scores.  
        - For larger PDFs, place files directly in sample_data/ and run `python -m src.cli ingest sample_data`.
        """,
        unsafe_allow_html=True,
    )

# Sidebar info
st.sidebar.markdown("### Demo Info")
st.sidebar.info("Local file-based RAG. Chunks persisted to db/chroma/chunks.json. TF-IDF index persisted via joblib.")
st.sidebar.markdown("**Quick commands (terminal)**")
st.sidebar.code("python -m src.cli ingest sample_data")
st.sidebar.code("python -m src.cli index")
st.sidebar.code('python -m src.cli query "Create use cases for user signup" --debug')