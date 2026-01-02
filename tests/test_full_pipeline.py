import sys
sys.path.insert(0, 'src')
import logging
logging.basicConfig(level=logging. INFO)

from generate import generate
from retrieval import retrieve

query = 'Create use cases for user login with email and password'

print(f'Query: {query}\n')
print('Step 1: Retrieving evidence...\n')

# Retrieve evidence first
evidence = retrieve(query, top_k=3)
print(f'✓ Retrieved {len(evidence)} chunks\n')

print('Step 2: Generating use cases...\n')

# Generate
result = generate(query, evidence)

print('\n' + '='*60)
print('RESULT:')
print('='*60)

import json
print(json. dumps(result, indent=2))

# Also save to file
with open('output.json', 'w') as f:
    json.dump(result, f, indent=2)
print('\n✓ Saved to output.json')
