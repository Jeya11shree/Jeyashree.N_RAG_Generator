#!/usr/bin/env python3
"""
test_ocr.py

Example/test script that demonstrates using src/ocr.py
Usage:
  python test_ocr.py path/to/input.pdf -o out.txt
"""

import argparse
from pathlib import Path
from src import ocr

def main():
    parser = argparse.ArgumentParser(description="Test OCR on a file (image or PDF)")
    parser.add_argument("input", help="Input file (image or PDF)")
    parser.add_argument("-o", "--output", help="Output text file (optional)")
    parser.add_argument("--dpi", type=int, default=200, help="DPI for PDFs")
    parser.add_argument("--lang", default="eng", help="Tesseract language")
    parser.add_argument("--no-preprocess", dest="preprocess", action="store_false", help="Disable preprocessing")
    parser.add_argument("--poppler-path", dest="poppler_path", default=None, help="Path to poppler (Windows)")
    args = parser.parse_args()

    out_text = ocr.extract_text(args.input, output_path=args.output, dpi=args.dpi, lang=args.lang,
                               preprocess=args.preprocess, poppler_path=args.poppler_path)
    if not args.output:
        print(out_text)
    else:
        print(f"Saved OCR text to {args.output}")

if __name__ == "__main__":
    main()
