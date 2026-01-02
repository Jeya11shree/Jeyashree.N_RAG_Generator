import json
from pathlib import Path

data = json.loads(Path('data/index.json').read_text(encoding='utf-8'))
print(f'Total chunks: {len(data)}')
print(f'Sources: {set(c["source"] for c in data)}')
print(f'\nFirst chunk preview:')
if data:
    print(data[0]['text'][:200])
