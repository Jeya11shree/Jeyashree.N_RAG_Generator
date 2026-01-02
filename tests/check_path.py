from pathlib import Path

# What's defined in retrieval.py
chunks_path_with_space = Path('db/chroma/chunks.  json')  # Has space
chunks_path_correct = Path('db/chroma/chunks.json')      # No space

print(f'Path with space exists: {chunks_path_with_space.exists()}')
print(f'Path without space exists: {chunks_path_correct.exists()}')

# Check actual file
import os
actual_files = list(Path('db/chroma').glob('*. json'))
print(f'\nActual files in db/chroma: {[f.name for f in actual_files]}')
