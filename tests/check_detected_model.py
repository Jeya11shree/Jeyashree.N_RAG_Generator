import sys
sys.path.insert(0, 'src')
from generate import _OLLAMA_AVAILABLE, _OLLAMA_MODEL

print(f'Ollama Available: {_OLLAMA_AVAILABLE}')
print(f'Model Detected:  {_OLLAMA_MODEL}')
