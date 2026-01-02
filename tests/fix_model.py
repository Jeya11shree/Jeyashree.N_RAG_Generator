from pathlib import Path
import re

filepath = Path('src/generate.py')
content = filepath.read_text(encoding='utf-8')

print('Current model references:')
if '1b' in content. lower():
    print('  Found 1b references')
if '3b' in content.lower():
    print('  Found 3b references')

# Replace model name everywhere
content = content.replace('llama3.2:1b', 'llama3.2:3b')
content = content.replace("'1b'", "'3b'")
content = content.replace('"1b"', '"3b"')

# Save
filepath.write_text(content, encoding='utf-8')
print('\n✓ Updated generate.py')

# Verify
content_check = filepath.read_text(encoding='utf-8')
if 'llama3.2:3b' in content_check and 'llama3.2:1b' not in content_check:
    print('✓ Confirmed:  Now using 3B')
else:
    print('⚠ Please check generate.py manually')
    print(f'  3b found: {"llama3.2:3b" in content_check}')
    print(f'  1b found: {"llama3.2:1b" in content_check}')
