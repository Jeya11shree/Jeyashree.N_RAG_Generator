import sys
sys.path.insert(0, 'src')
import logging
logging.basicConfig(level=logging. INFO)

from generate import generate_use_cases

query = 'Create use cases for user login'

print(f'Query: {query}\n')
print('Generating.. .\n')

result = generate_use_cases(query)

print('\n' + '='*60)
print('RESULT:')
print('='*60)

import json
print(json.dumps(result, indent=2))
