import sys
sys.path.insert(0, 'src')
import requests
import json

print('Testing with STREAMING...\n')

simple_prompt = 'Say hello in JSON format:  {\"message\": \"your response\"}'

response = requests.post(
    'http://localhost:11434/api/generate',
    json={
        'model':  'phi3.5:latest',
        'prompt':  simple_prompt,
        'stream':  True  # Enable streaming
    },
    stream=True,
    timeout=60
)

full_response = ''
for line in response.iter_lines():
    if line:
        chunk = json.loads(line)
        if 'response' in chunk: 
            full_response += chunk['response']
            print(chunk['response'], end='', flush=True)
        if chunk.get('done'):
            break

print(f'\n\nFull response:\n{full_response}')
