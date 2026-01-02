from pathlib import Path

content = Path('src/generate.py').read_text(encoding='utf-8', errors='ignore')

# Find the _build_prompt function and update the system message
old_system = 'You are a test case generator'

new_system = '''You are a JSON-only test case generator. You MUST respond with ONLY valid JSON.

CRITICAL RULES:
1. Output MUST start with { and end with }
2. NO explanations before or after the JSON
3. NO markdown code blocks
4. NO extra text
5. ONLY valid JSON structure'''

content = content.replace(old_system, new_system)

Path('src/generate.py').write_text(content, encoding='utf-8')
print('✓ Updated system prompt')
