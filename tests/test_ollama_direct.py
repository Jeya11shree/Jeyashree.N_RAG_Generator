import requests
import json

print('Testing Ollama API from Python...\n')

# Test 1: Check if API is up
try:
    response = requests.get('http://localhost:11434/api/tags', timeout=5)
    print(f'✓ API is up: {response.status_code}')
    print(f'  Models: {[m["name"] for m in response.json()["models"]]}\n')
except Exception as e:
    print(f'✗ API not responding: {e}\n')
    exit()

# Test 2: Simple generation
print('Testing generation (30 seconds)...')
try:
    payload = {
        'model': 'phi3.5',
        'prompt': 'Say hello in one sentence',
        'stream': False
    }
    
    response = requests.post(
        'http://localhost:11434/api/generate',
        json=payload,
        timeout=60
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f'✓ Generation successful!')
        print(f'  Response: {result. get("response", "")[: 100]}...')
    else:
        print(f'✗ Generation failed: {response.status_code}')
        print(f'  Error: {response.text}')
        
except Exception as e:
    print(f'✗ Generation error: {e}')
