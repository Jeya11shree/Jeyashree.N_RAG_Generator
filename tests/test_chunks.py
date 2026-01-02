from src import retrieval
from pathlib import Path
import json

# Direct test
chunks_path = Path('db/chroma/chunks.json')
chunks = json.loads(chunks_path. read_text())

print(f'Chunks in file: {len(chunks)}')
print(f'Chunks keys: {list(chunks[0].keys())}')

# Check what _load_chunks returns
loaded = retrieval._load_chunks()
print(f'\n_load_chunks() returned: {len(loaded)} chunks')

# Check global state
print(f'\n_CHUNKS global:  {retrieval._CHUNKS}')
print(f'_EMBEDDINGS global: {retrieval._EMBEDDINGS}')
print(f'_MODEL global: {retrieval._MODEL}')
