import requests
import json

print('Testing FULL pipeline with minimal prompt\n')

# Minimal test case generation prompt
prompt = '''Generate test cases in JSON format for:  user login

Output ONLY this JSON structure, no other text:
{
  \"use_cases\": [
    {
      \"title\": \"Valid Login\",
      \"steps\": [\"Enter username\", \"Enter password\", \"Click login\"],
      \"expected_outcome\": \"User logged in\",
      \"negative_cases\": [\"Wrong password\"],
      \"boundary_cases\": [\"Empty password\"],
      \"assumptions\": [\"User exists\"]
    }
  ]
}'''

print(f'Prompt: {prompt}\n')

response = requests.post(
    'http://localhost:11434/api/generate',
    json={
        'model': 'phi3.5:latest',
        'prompt': prompt,
        'stream': True,
        'options':  {'temperature': 0.2, 'num_predict': 1000}
    },
    stream=True,
    timeout=120
)

full_response = ''
print('Response:  ', end='', flush=True)
for line in response.iter_lines():
    if line:
        chunk = json.loads(line)
        if 'response' in chunk: 
            full_response += chunk['response']
            print(chunk['response'], end='', flush=True)
        if chunk.get('done'):
            break

print(f'\n\nFull response length: {len(full_response)} chars')

# Extract JSON
import re
json_match = re.search(r'\{.*\}', full_response, re.DOTALL)
if json_match:
    try:
        result = json.loads(json_match.group())
        print(f'\n✓ SUCCESS: {result}')
    except: 
        print(f'\n✗ Invalid JSON: {json_match.group()[:200]}')
else:
    print('\n✗ No JSON found')
