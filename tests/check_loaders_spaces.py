from pathlib import Path

content = Path('src/loaders.py').read_text(encoding='utf-8')

# Find the line with . txt check
for i, line in enumerate(content. split('\n')[:30], 1):
    if '.txt' in line or 'suffix' in line. lower():
        print(f'Line {i}: {repr(line)}')
