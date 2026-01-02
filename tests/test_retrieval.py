from src import retrieval

print('Testing retrieval...\n')

retrieval.run_build_index()
r = retrieval.retrieve('classic tea', top_k=1)

if r:
    print(f'✓ Retrieval working!')
    print(f'  Score: {r[0]["score"]:.3f}')
    print(f'  Semantic:  {r[0]["semantic_score"]:.3f}')
    print(f'  Source: {r[0]["source"]}')
else:
    print('✗ No results')
