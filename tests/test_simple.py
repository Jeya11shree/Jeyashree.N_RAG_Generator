from src import retrieval, generate

print('Testing with simpler query...\n')

retrieval.run_build_index()
chunks = retrieval.retrieve('tea', top_k=1)

print(f'Retrieved:  {len(chunks)} chunks\n')

# Simpler prompt
print('Calling Phi-3 (60 seconds)...\n')
result = generate.generate('List 3 steps to make tea', chunks)

if result['status'] == 'success':  
    print('✅ SUCCESS!')
    print(f'Use cases: {len(result["use_cases"])}')
    
    if result['use_cases']:
        uc = result['use_cases'][0]
        print(f'\nTitle: {uc["title"]}')
        print(f'Steps: ')
        for i, step in enumerate(uc['steps'], 1):
            print(f'  {i}.  {step}')
else:
    print(f'❌ Failed: {result. get("message")}')
