import sys
sys.path.insert(0, 'src')
import requests

print('Testing raw Ollama output...\n')

simple_prompt = '''Generate JSON test cases for:  make tea

Output format:
{
  \"use_cases\": [{
    \"title\": \"Make Hot Tea\",
    \"steps\": [\"Boil water\", \"Add tea bag\", \"Steep 3 minutes\"],
    \"expected_outcome\": \"Hot tea ready\",
    \"negative_cases\": [\"No water\"],
    \"boundary_cases\":   [\"Cold water\"],
    \"assumptions\": [\"Tea bag available\"]
  }]
}'''

response = requests.post(
    'http://localhost:11434/api/generate',
    json={
        'model': 'phi3.5:latest',
        'prompt':  simple_prompt,
        'stream': False,
        'options':  {
            'temperature': 0.2,
            'num_predict': 2000
        }
    },
    timeout=60
)

result = response.json()
print('RAW OUTPUT FROM PHI-3:')
print('='*60)
print(result.get('response', ''))
print('='*60)
