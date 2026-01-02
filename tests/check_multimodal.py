import sys
from pathlib import Path

print('=== CHECKING MULTIMODAL SUPPORT ===\n')

# Check loaders.py
loaders_file = Path('src/loaders.  py')
if loaders_file.exists():
    content = loaders_file.read_text()
    
    print('1. Text loader:', 'load_text' in content)
    print('2. PDF loader:', 'load_pdf' in content and 'pdfminer' in content)
    print('3. DOCX loader:', 'load_docx' in content and 'docx' in content)
    print('4. Image loader:', 'load_image' in content)
    print('5. OCR support:', 'pytesseract' in content or 'ocr' in content)
    
    # Check imports
    print('\nImports found:')
    for line in content.split('\n')[:30]:
        if 'import' in line and not line.strip().startswith('#'):
            print(f'   {line. strip()}')
else:
    print('✗ loaders.  py NOT FOUND')

# Check if ingest.py uses these loaders
print('\n')
ingest_file = Path('src/ingest.py')
if ingest_file.exists():
    content = ingest_file.read_text()
    print('ingest.py calls loaders:', 'from src import loaders' in content or 'from .  import loaders' in content)
else:
    print('✗ ingest.py NOT FOUND')
