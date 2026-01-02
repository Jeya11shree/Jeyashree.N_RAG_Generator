from src import retrieval
import json
from pathlib import Path

print('=== DEBUGGING RETRIEVAL ===\n')

# Check 1: Chunks file
chunks_path = Path('db/chroma/chunks.json')
print(f'1. Chunks file exists: {chunks_path.exists()}')

if chunks_path.exists():
    chunks = json.loads(chunks_path. read_text())
    print(f'   Chunks count:  {len(chunks)}')
    if chunks:
        print(f'   First chunk source: {chunks[0].get("source")}')
        print(f'   First chunk length: {len(chunks[0]. get("text", ""))} chars')
else:
    print('   ERROR: No chunks file!  Run ingestion first.')
    exit()

# Check 2: Build index
print(f'\n2. Building index...')
model, embeddings, loaded_chunks = retrieval.run_build_index()

print(f'   Model loaded: {model is not None}')
print(f'   Embeddings created: {embeddings is not None}')
print(f'   Chunks loaded: {len(loaded_chunks) if loaded_chunks else 0}')

# Check 3: Retrieve
if loaded_chunks:
    print(f'\n3. Testing retrieval.. .')
    results = retrieval. retrieve('classic tea', top_k=1)
    
    print(f'   Results returned: {len(results)}')
    
    if results:
        print(f'   Top score: {results[0]["score"]:.3f}')
        print(f'   Semantic:  {results[0]["semantic_score"]:.3f}')
        print(f'   Source: {results[0]["source"]}')
    else:
        print(f'   No results returned')
else:
    print(f'\nNo chunks loaded')
