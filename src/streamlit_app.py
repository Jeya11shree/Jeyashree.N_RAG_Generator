from dotenv import load_dotenv
load_dotenv()
import streamlit as st, json, time, tempfile
from pathlib import Path
import shutil

from ingest import ingest_files
from retrieval import retrieve
from generate import generate

def save_uploaded_files(uploaded_files):
    temp_dir = Path(tempfile.mkdtemp(prefix='rag_uploads_'))
    for file in uploaded_files:
        file_path = temp_dir / file.name
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
    return temp_dir

st.set_page_config(page_title='RAG Test Case Generator', page_icon='🤖', layout='wide')
st.markdown('<h1 style="text-align:center; background: #1e90ff; color:white; padding:0.4em 0;">RAG Test Case Generator</h1>', unsafe_allow_html=True)

#Track session state
if "uploaded_dir" not in st.session_state:
    st.session_state.uploaded_dir = None
    st.session_state.chunks = []
    st.session_state.results = None

with st.sidebar:
    st.header('Document Upload')
    uploaded_files = st.file_uploader(
        'Select files to upload',
        type=['txt','md','pdf','docx','png','jpg','jpeg'],
        accept_multiple_files=True)
    if uploaded_files:
        st.info(f"{len(uploaded_files)} file(s) selected.")
        if st.button('Ingest Uploaded Files'):
            if st.session_state.uploaded_dir:
                shutil.rmtree(st.session_state.uploaded_dir, ignore_errors=True)
            with st.spinner("Ingesting..."):
                upload_dir = save_uploaded_files(uploaded_files)
                st.session_state.uploaded_dir = str(upload_dir)
                file_paths = list(upload_dir.glob("*"))
                st.session_state.chunks = ingest_files(file_paths)
                st.session_state.results = None
                st.success(f"Ingested {len(file_paths)} files!")
                time.sleep(1)
                st.rerun()
    if st.button('Clear Session KB'):
        if st.session_state.uploaded_dir:
            shutil.rmtree(st.session_state.uploaded_dir, ignore_errors=True)
        st.session_state.uploaded_dir = None
        st.session_state.chunks = []
        st.session_state.results = None
        st.success("Session KB cleared. Ready for new uploads!")
    st.header('Settings')
    top_k = st.slider('Retrieved Chunks (top_k)', 3, 10, 5)
    show_debug = st.checkbox('Debug mode')
    st.markdown(f'**Total Indexed Chunks:** {len(st.session_state.chunks)}')

st.markdown('#### Enter Your Query')
query = st.text_area('Query', "", placeholder='E.g. Create use cases for user signup', height=100, label_visibility='collapsed')
col_btn1, col_btn2 = st.columns([4,1])
with col_btn1: generate_btn = st.button('Generate')
with col_btn2:
    if st.session_state.results:
        st.download_button('Download JSON', json.dumps(st.session_state.results['output_json'], indent=2), 'result.json', 'application/json')

if generate_btn and query.strip():
    st.markdown('<hr>', unsafe_allow_html=True)
    with st.spinner('Retrieving...'):
        try:
            chunks = retrieve(query, st.session_state.chunks, top_k=top_k)
            st.success(f"Retrieved {len(chunks)} relevant chunks.")
            if show_debug:
                with st.expander('Retrieved Evidence Chunks'):
                    for i, c in enumerate(chunks,1):
                        st.write(f"Chunk {i}: {c.get('source','?')} | Score: {c.get('score',0):.3f}")
                        st.write(c.get('text','')[:300]+"..."); st.divider()
        except Exception as e:
            st.error(f'Retrieval error: {e}')
            chunks = []
    with st.spinner('Generating with AI...' if chunks else 'No relevant evidence, asking for clarifications...'):
        try:
            result = generate(query, chunks)
            st.session_state.results = result
            st.success(f"Generated using {result.get('model_used','?')} (status: {result.get('status','')})")
        except Exception as e: st.error(f"Generation error: {e}")

if st.session_state.results:
    result = st.session_state.results
    st.markdown('<hr>', unsafe_allow_html=True)
    st.header('Generated Result')
    tab1, tab2 = st.tabs(['Formatted View','JSON'])
    with tab1:
        val = result.get("output_json")
        if val:
            st.subheader("Test/Use Cases")
            st.json(val)
        else:
            st.info("No recognized fields or output is empty.")
            st.json(result)
    with tab2:
        st.json(result)
    if 'evidence_summary' in result:
        st.write("Evidence Sources:")
        for ev in result['evidence_summary']:
            st.write(f"{ev.get('source','?')} (score: {ev.get('score',0):.3f})")