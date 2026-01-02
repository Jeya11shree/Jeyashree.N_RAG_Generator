import sys
sys.path.insert(0, 'src')
from pathlib import Path

content = Path('src/generate.py').read_text(encoding='utf-8', errors='ignore')

# Replace the _call_ollama function
new_function = '''def _call_ollama(prompt:  str, model: str) -> dict:
    \"\"\"Call Ollama API with streaming. \"\"\"
    try:
        response = requests.post(
            \"http://localhost:11434/api/generate\",
            json={
                \"model\": model,
                \"prompt\": prompt,
                \"stream\": True,  # Enable streaming to avoid timeout
                \"options\": {
                    \"temperature\": 0.2,
                    \"num_predict\": 2000,
                    \"top_p\": 0.9
                }
            },
            stream=True,
            timeout=300
        )

        if response.status_code != 200:
            raise Exception(f\"Ollama error: {response.text}\")

        # Collect streamed response
        full_response = ''
        for line in response.iter_lines():
            if line: 
                chunk = json.loads(line)
                if 'response' in chunk:
                    full_response += chunk['response']
                if chunk.get('done'):
                    break

        generated_text = full_response.strip()
        logger.info(f\"Generated {len(generated_text)} chars\")

        # Extract JSON from response
        generated_text = _extract_json(generated_text)

        result = json.loads(generated_text)
        return result

    except json.JSONDecodeError as e:
        logger.error(f\"Invalid JSON:  {e}\")
        return {\"status\": \"error\", \"message\": \"Invalid JSON\", \"use_cases\": []}
    except Exception as e:
        logger.error(f\"Ollama call failed: {e}\")
        return {\"status\": \"error\", \"message\": str(e), \"use_cases\": []}'''

# Find and replace the function
import re
pattern = r'def _call_ollama\(.*?\n(? :.*?\n)*?(?=\ndef |$)'
content = re.sub(pattern, new_function + '\n\n', content, count=1, flags=re.MULTILINE)

Path('src/generate.py').write_text(content, encoding='utf-8')
print('✓ Updated _call_ollama to use streaming')
