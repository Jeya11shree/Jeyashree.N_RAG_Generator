"""Test ingestion manually."""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src import ingest
from src.chunking import chunk_text
from src.loaders import load_file

# Test loading the file
file_path = Path("sample_data_uploads/recipe_tea.txt")

print("=" * 60)
print("Testing file loading...")
print("=" * 60)

if file_path.exists():
    print(f"✓ File exists: {file_path}")
    print(f"✓ File size: {file_path.stat().st_size} bytes")
    
    # Test loading
    text = load_file(file_path)
    print(f"✓ Extracted text length: {len(text)} characters")
    print(f"\nFirst 200 chars:\n{text[:200]}\n")
    
    # Test chunking
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    print(f"✓ Generated {len(chunks)} chunks")
    
    if chunks:
        print(f"\nFirst chunk preview:\n{chunks[0][: 200]}\n")
    else:
        print("❌ No chunks generated!")
        
        # Debug chunking
        words = text.split()
        print(f"Word count: {len(words)}")
        
        if len(words) < 50:
            print("⚠️ Text too short for default min_chunk_size (50 words)")
            print("Trying with smaller min_chunk_size...")
            chunks = chunk_text(text, chunk_size=500, overlap=50, min_chunk_size=10)
            print(f"✓ Generated {len(chunks)} chunks with min_chunk_size=10")
    
    # Test full ingestion
    print("\n" + "=" * 60)
    print("Testing full ingestion pipeline...")
    print("=" * 60)
    
    result = ingest.run(
        input_path="sample_data_uploads",
        persist=True,
        clear_existing=True
    )
    
    print(f"\n✓ Ingestion result: {len(result)} chunks")
    
    if result:
        print("\nSample chunk:")
        print(result[0])
else:
    print(f"❌ File not found: {file_path}")