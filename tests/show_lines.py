from pathlib import Path
content = Path('src/generate.py').read_text(encoding='utf-8', errors='ignore')
lines = content.split('\n')
for i in range(84, 121):
    if i < len(lines):
        print(f'{i+1}:  {lines[i]}')
