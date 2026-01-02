import sys
sys.path.insert(0, 'src')
import requests
import json

# Test what Phi-3 actually returns
response = requests.post(
    'http://localhost:11434/api/generate',
    json={'model': 'phi3.5:latest', 'prompt': 'Say hello', 'stream': True},
    stream=True,
    timeout=60
)

full_response = ''
for line in response.iter_lines():
    if line:
        chunk = json.loads(line)
        if 'response' in chunk: 
            full_response += chunk['response']
        if chunk.get('done'):
            break

print('RAW OUTPUT:')
print(full_response)
print('\n\nTrying to find JSON...')

# Try to extract JSON
import re
json_match = re.search(r'\{.*\}', full_response, re.DOTALL)
if json_match:
    print('Found JSON:', json_match.group())
else:
    print('NO JSON FOUND')
