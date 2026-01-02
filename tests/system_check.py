from pathlib import Path
import json

print('=== SYSTEM CHECK ===')
print()

# Check files
files = {
    'App':  'src/app.py',
    'Generate': 'src/generate. py',
    'Retrieval': 'src/retrieval. py',
    'Ingest': 'src/ingest. py',
    'Index': 'data/index. json',
    'Template': 'src/templates/index.html'
}

for name, path in files.items():
    exists = Path(path).exists()
    status = 'OK' if exists else 'MISSING'
    print('[' + status + '] ' + name. ljust(12) + ' -> ' + path)

# Check index
print()
print('=== INDEX STATUS ===')
if Path('data/index.json').exists():
    data = json.loads(Path('data/index.json').read_text(encoding='utf-8'))
    print('Total chunks: ' + str(len(data)))
    sources = set(c['source'] for c in data)
    print('Sources:  ' + str(sources))
else:
    print('[ERROR] No index found')

# Check model in generate. py
print()
print('=== MODEL CONFIG ===')
gen_content = Path('src/generate.py').read_text()
if 'llama3.2:3b' in gen_content:
    print('[OK] Using Llama 3.2 3B')
elif 'llama3.2:1b' in gen_content:
    print('[ERROR] Still using 1B')
else:
    print('[WARNING] Model not found in generate. py')

print()
print('=== READY TO START ===')
print('Run: python src\\app.py')
