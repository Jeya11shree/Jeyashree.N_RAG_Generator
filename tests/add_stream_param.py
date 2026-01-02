from pathlib import Path

content = Path('src/generate.py').read_text(encoding='utf-8', errors='ignore')

# Find and fix the requests.post call
# Add stream=True parameter after json={... }
old_code = '''            json={
                "model":  model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 2000,
                    "top_p": 0.9
                }
            },
            timeout=300'''

new_code = '''            json={
                "model":  model,
                "prompt": prompt,
                "stream": True,
                "options":  {
                    "temperature": 0.2,
                    "num_predict": 2000,
                    "top_p":  0.9
                }
            },
            stream=True,
            timeout=300'''

content = content.replace(old_code, new_code)

Path('src/generate.py').write_text(content, encoding='utf-8')
print('✓ Added stream=True parameter to requests.post()')
