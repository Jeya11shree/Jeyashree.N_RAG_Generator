import sys
sys.path.insert(0, 'src')
from generate import _call_ollama

print('Testing _call_ollama with simple prompt...\n')

simple_prompt = '''Generate JSON test cases for:  make tea

Output format:
{
  \"use_cases\": [{
    \"title\": \"Make Hot Tea\",
    \"steps\": [\"Boil water\", \"Add tea bag\", \"Steep 3 minutes\"],
    \"expected_outcome\": \"Hot tea ready\",
    \"negative_cases\": [\"No water\"],
    \"boundary_cases\":  [\"Cold water\"],
    \"assumptions\": [\"Tea bag available\"]
  }]
}'''

print(f'Prompt length: {len(simple_prompt)} chars\n')
print('Calling Ollama...  (may take 30-60 seconds)\n')

result = _call_ollama(simple_prompt, 'phi3.5:latest')

print(f'Result: {result}')
