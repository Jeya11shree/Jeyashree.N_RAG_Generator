from pathlib import Path
content = Path('src/generate.py').read_text(encoding='utf-8', errors='ignore')
lines = content.split('\n')

in_function = False
for i, line in enumerate(lines, 1):
    if 'def _call_ollama' in line: 
        in_function = True
    if in_function:
        print(f'{i}: {line}')
        if line.strip() and not line.strip().startswith('#') and i > 0:
            # Stop after function ends (next def or class)
            if 'def ' in lines[i] if i < len(lines) else False:
                break
