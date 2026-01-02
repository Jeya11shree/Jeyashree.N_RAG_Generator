from pathlib import Path

content = Path('src/generate.py').read_text(encoding='utf-8', errors='ignore')

# Find where we build the prompt and add strict JSON format requirement
# Look for the return statement in _build_prompt

# Add this template at the end of prompts
json_template = '''

OUTPUT FORMAT (copy this structure exactly):
{
  "use_cases": [
    {
      "title": "string",
      "goal": "string",
      "preconditions":  ["string"],
      "test_data": {},
      "steps": ["string"],
      "expected_results": ["string"],
      "negative_cases": ["string"],
      "boundary_cases": ["string"],
      "assumptions": ["string"]
    }
  ]
}

START YOUR RESPONSE WITH { AND END WITH }.  NO OTHER TEXT.'''

# Find the last line before 'return prompt' in _build_prompt
lines = content.split('\n')
new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    # If this line has 'prompt +=' and next line has 'return prompt'
    if 'CRITICAL:  You MUST respond' in line and i < len(lines) - 1:
        # Add JSON template before return
        indent = '    '
        new_lines.append(f'{indent}prompt += """{json_template}"""')

content = '\n'.join(new_lines)

Path('src/generate.py').write_text(content, encoding='utf-8')
print('✓ Added JSON template to prompt')
