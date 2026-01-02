from pathlib import Path
import re

content = Path('src/generate.py').read_text(encoding='utf-8', errors='ignore')

# Find _extract_json function
old_extract = '''def _extract_json(text:  str) -> str:
    \"\"\"Extract JSON from text. \"\"\"
    text = text.strip()
    
    # Remove markdown code blocks
    text = re. sub(r'`json\\s*', '', text)
    text = re.sub(r'`\\s*', '', text)
    
    # Find JSON object
    start = text.find('{')
    if start == -1:
        return text
    
    # Find matching closing brace
    brace_count = 0
    for i in range(start, len(text)):
        if text[i] == '{': 
            brace_count += 1
        elif text[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                return text[start:i+1]
    
    return text'''

new_extract = '''def _extract_json(text: str) -> str:
    \"\"\"Extract JSON from text with aggressive cleaning.\"\"\"
    text = text.strip()
    
    # Remove markdown code blocks
    text = re.sub(r'`[a-z]*\\s*', '', text, flags=re.IGNORECASE)
    
    # Remove common prefixes
    text = re.sub(r'^(Here|Sure|Certainly|Output|Result)[^{]*', '', text, flags=re.IGNORECASE)
    
    # Find FIRST { and LAST }
    start = text.find('{')
    end = text.rfind('}')
    
    if start == -1 or end == -1 or start >= end:
        logger.warning(f"No JSON found in:  {text[: 200]}")
        # Return minimal valid JSON
        return '{"status": "error", "message": "No JSON generated", "use_cases": []}'
    
    extracted = text[start:end+1]
    
    # Validate it's somewhat valid
    if extracted.count('{') != extracted.count('}'):
        logger.warning("Unbalanced braces, trying to fix...")
        # Try to balance
        open_count = extracted.count('{')
        close_count = extracted.count('}')
        if open_count > close_count:
            extracted += '}' * (open_count - close_count)
    
    return extracted'''

content = content.replace(old_extract, new_extract)

Path('src/generate.py').write_text(content, encoding='utf-8')
print('✓ Updated JSON extraction with aggressive cleaning')
