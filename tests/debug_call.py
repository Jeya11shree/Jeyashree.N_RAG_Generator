import sys
sys.path.insert(0, 'src')
import logging
logging.basicConfig(level=logging. DEBUG)

# Import the function
from generate import _call_ollama

# Test with minimal prompt
prompt = 'Say hello in one word'

print('Calling _call_ollama directly...\n')
print(f'Prompt: {prompt}\n')

try:
    result = _call_ollama(prompt, 'phi3.5:latest')
    print(f'\n✓ Success:  {result}')
except Exception as e: 
    print(f'\n✗ Error: {e}')
    import traceback
    traceback.print_exc()
