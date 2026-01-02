from pathlib import Path
content = Path('src/generate.py').read_text(encoding='utf-8', errors='ignore')

# Find the ollama call
lines = content.split('\n')
for i, line in enumerate(lines, 1):
    if 'ollama' in line. lower() or 'localhost: 11434' in line or 'requests.' in line:
        print(f'{i}:  {line}')
