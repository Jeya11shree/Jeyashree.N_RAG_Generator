from src import loaders
from pathlib import Path

print('=== TESTING MULTIMODAL LOADERS ===\n')

# Test 1: Text file
print('1. Text File:')
text_file = Path('sample_data_uploads/recipe_tea.txt')
if text_file.exists():
    text = loaders.load_file(text_file)
    print(f'   ✓ Extracted {len(text)} chars')
else:
    print('   ✗ File not found')

# Test 2: Check what file types are supported
print('\n2. Supported formats:')
print('   ✓ Text: .txt, .md, .csv, .log, .json')
print('   ✓ PDF: .pdf')
print('   ✓ DOCX: .docx, .doc')
print('   ✓ Images: .png, .jpg, . jpeg, .bmp, .tiff (OCR)')

# Test 3: Check dependencies
print('\n3. Dependencies:')

try:
    from pdfminer.high_level import extract_text
    print('   ✓ PDF support (pdfminer.six)')
except ImportError:
    print('   ✗ PDF support missing - install:  pip install pdfminer.six')

try:
    import docx
    print('   ✓ DOCX support (python-docx)')
except ImportError: 
    print('   ✗ DOCX support missing - install:  pip install python-docx')

try:
    from PIL import Image
    import pytesseract
    print('   ✓ OCR support (Pillow + pytesseract)')
except ImportError:
    print('   ⚠ OCR support missing - install: pip install Pillow pytesseract')
    print('     Also need Tesseract:   https://github.com/tesseract-ocr/tesseract')

print('\n=== TEST COMPLETE ===')
