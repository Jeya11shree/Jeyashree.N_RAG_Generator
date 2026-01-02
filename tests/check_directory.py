from pathlib import Path

directory = Path('sample_data_uploads')

print('=== CHECKING DIRECTORY ===\n')
print(f'Directory exists: {directory.exists()}\n')

if directory.exists():
    print('All items in directory:')
    for item in directory.iterdir():
        print(f'  - {item.name} (is_file: {item.is_file()}, suffix: {item.suffix})')
    
    print('\nFiltering for . txt files:')
    txt_files = list(directory.glob('*.txt'))
    print(f'  Found {len(txt_files)} .txt files:  {[f.name for f in txt_files]}')
