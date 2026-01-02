from pathlib import Path

# Read the file
content = Path('src/generate.py').read_text(encoding='utf-8', errors='ignore')
lines = content.split('\n')

# Find the lines to replace (105-107 in 0-indexed:  105-106)
new_lines = lines[: 105]  # Everything before line 106

# Add new streaming code
new_lines.extend([
    '        # Collect streamed response',
    "        full_response = ''",
    '        for line in response.iter_lines():',
    '            if line: ',
    '                chunk = json.loads(line)',
    "                if 'response' in chunk:",
    "                    full_response += chunk['response']",
    "                if chunk. get('done'):",
    '                    break',
    '        ',
    '        generated_text = full_response.strip()'
])

# Add everything after line 108 (0-indexed: skip 106-107, continue from 108)
new_lines.extend(lines[108:])

# Write back
Path('src/generate.py').write_text('\n'.join(new_lines), encoding='utf-8')
print('✓ Fixed streaming in generate.py')
