import requests
import json

print('Direct streaming test.. .\n')

response = requests. post(
    'http://localhost:11434/api/generate',
    json={
        'model': 'phi3.5:latest',
        'prompt': 'Say hello',
        'stream': True
    },
    stream=True,
    timeout=60
)

print(f'Status: {response.status_code}')
print(f'Headers: {response.headers. get("content-type")}')
print('\nReading stream.. .')

count = 0
for line in response.iter_lines():
    if line:
        count += 1
        chunk = json.loads(line)
        print(f'{chunk.get("response", "")}', end='', flush=True)
        if chunk.get('done'):
            print(f'\n\n✓ Completed in {count} chunks')
            break
