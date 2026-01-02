from pathlib import Path

content = Path('src/generate.py').read_text(encoding='utf-8', errors='ignore')

# Find _build_prompt function and make it stricter
old_return = 'return prompt'

# Add this before return
strict_json = '''
    # Force JSON output
    prompt += \"\"\"

CRITICAL: You MUST respond with ONLY valid JSON. No explanations, no markdown, no extra text. 
Start with { and end with }. Nothing else.
\"\"\"
    return prompt'''

content = content.replace('    return prompt', strict_json)

Path('src/generate.py').write_text(content, encoding='utf-8')
print('✓ Updated prompt to force JSON')
