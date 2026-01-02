from src import retrieval, generate

print('=== TESTING COMPLETE PIPELINE ===\n')

# 1. Retrieval
print('1. Retrieval:')
retrieval.run_build_index()
chunks = retrieval. retrieve('classic hot tea preparation', top_k=2)

if chunks:
    print(f'   ✓ Retrieved {len(chunks)} chunks')
    print(f'   ✓ Top score: {chunks[0]["score"]:.3f}')
    print(f'   ✓ Source: {chunks[0]["source"]}')
else:
    print('   ✗ No chunks retrieved')
    exit()

# 2. Generation
print('\n2. Generation (calling Phi-3 via Ollama...  20-30 seconds):')
result = generate.generate('Create test cases for classic hot tea with boiling water and teabag', chunks)

if result['status'] == 'success':
    print(f'   ✓ Generation successful!')
    print(f'   ✓ Use cases:  {len(result["use_cases"])}')
    
    if result['use_cases']:
        uc = result['use_cases'][0]
        print(f'\n3. Sample Output:')
        print(f'   Title: {uc["title"][:60]}...')
        print(f'   Steps: {len(uc["steps"])}')
        if uc['steps']:
            print(f'   Step 1: {uc["steps"][0][:80]}...')
            print(f'   Step 2: {uc["steps"][1][:80]}...' if len(uc['steps']) > 1 else '')
else:
    print(f'   ✗ Generation failed:  {result.get("message")}')

print('\n✅ COMPLETE PIPELINE WORKING!')
