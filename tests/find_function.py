from pathlib import Path
content = Path('src/generate.py').read_text(encoding='utf-8', errors='ignore')
lines = content.split('\n')

start = None
end = None
for i, line in enumerate(lines):
    if 'def _call_ollama' in line: 
        start = i
    if start is not None and i > start and line.strip() and not line.startswith(' ') and not line.startswith('\t'):
        end = i
        break

if start: 
    print(f'Function starts at line {start+1}')
    print(f'Function ends around line {end+1 if end else len(lines)}')
    print('\nCurrent function: ')
    print('='*60)
    for i in range(start, (end if end else start+30)):
        print(f'{i+1}:  {lines[i]}')
