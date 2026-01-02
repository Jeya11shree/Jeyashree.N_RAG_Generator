from pathlib import Path
content = Path('src/generate.py').read_text(encoding='utf-8', errors='ignore')
lines = content.split('\n')

in_function = False
brace_count = 0
for i, line in enumerate(lines, 1):
    if 'def _build_prompt' in line:
        in_function = True
    if in_function: 
        print(f'{i}: {line}')
