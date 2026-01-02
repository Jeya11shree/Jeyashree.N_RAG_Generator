from pathlib import Path

ingest_path = Path('src/ingest.py')
content = ingest_path.read_text(encoding='utf-8', errors='ignore')

# Find how it calls loaders
print('=== CHECKING INGEST.PY ===\n')

if 'from src import loaders' in content or 'from .  import loaders' in content: 
    print('✓ Imports loaders correctly')
else:
    print('✗ Loaders import issue')

if 'loaders.load_file' in content: 
    print('✓ Calls loaders.load_file()')
else:
    print('✗ Does not call loaders.load_file()')

# Show the loader call section
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'load' in line.lower() and 'loader' in line.lower():
        print(f'\nLine {i}:  {line}')
