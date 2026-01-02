from pathlib import Path
content = Path('src/generate.py').read_text(encoding='utf-8', errors='ignore')
for i, line in enumerate(content. split('\n'), 1):
    if 'timeout' in line. lower():
        print(f'Line {i}: {line}')
