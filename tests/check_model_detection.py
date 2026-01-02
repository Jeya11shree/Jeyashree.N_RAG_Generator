from pathlib import Path
content = Path('src/generate.py').read_text(encoding='utf-8', errors='ignore')

# Find model detection lines
lines = content.split('\n')
for i, line in enumerate(lines, 1):
    if 'phi3' in line. lower() and ('model' in line. lower() or 'mini' in line.lower()):
        print(f'{i}: {line}')
