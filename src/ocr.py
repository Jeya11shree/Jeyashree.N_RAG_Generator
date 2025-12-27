#!/usr/bin/env python3
"""
src/ocr.py

OCR helpers:
- ocr_image(path_or_pil_image, preprocess=True, lang='eng')
- ocr_pdf(pdf_path, dpi=200, lang='eng') with a fallback to PyMuPDF if Poppler/pdf2image is unavailable
- extract_text(...) high-level wrapper
"""
from pathlib import Path
from typing import List, Union, Tuple

from PIL import Image, ImageOps, ImageFilter
import pytesseract

# pdf2image may require Poppler on the system
try:
    from pdf2image import convert_from_path
    _has_pdf2image = True
except Exception:
    convert_from_path = None
    _has_pdf2image = False

# OpenCV for more advanced preprocessing; optional
try:
    import cv2
    _cv2_available = True
except Exception:
    _cv2_available = False

# PyMuPDF (pymupdf) for fallback PDF rendering
try:
    import fitz  # PyMuPDF
    _has_pymupdf = True
except Exception:
    fitz = None
    _has_pymupdf = False


def _is_pdf(path: Union[str, Path]) -> bool:
    p = Path(path)
    return p.suffix.lower() == ".pdf"


def _preprocess_pil_image(img: Image.Image, use_cv: bool = True) -> Image.Image:
    """
    Basic preprocessing to improve OCR accuracy:
    - convert to grayscale
    - increase contrast / auto-level
    - optional OpenCV denoise + thresholding if opencv-python is installed
    """
    img = img.convert("L")
    img = img.filter(ImageFilter.SHARPEN)
    try:
        img = ImageOps.autocontrast(img)
    except Exception:
        pass

    if _cv2_available and use_cv:
        import numpy as np
        arr = np.array(img)
        try:
            arr = cv2.fastNlMeansDenoising(arr, None, 7, 21, 7)
        except Exception:
            pass
        try:
            arr = cv2.adaptiveThreshold(arr, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY, 31, 2)
            img = Image.fromarray(arr)
        except Exception:
            pass

    return img


def ocr_image(image_input: Union[str, Path, Image.Image],
              lang: str = "eng",
              preprocess: bool = True,
              psm: int = 3,
              oem: int = 3,
              config_extra: str = "") -> str:
    """
    Run OCR on an image (file path or PIL Image).
    """
    if isinstance(image_input, (str, Path)):
        image_input = Image.open(str(image_input))

    img = image_input
    if preprocess:
        img = _preprocess_pil_image(img)

    config = f'--psm {psm} --oem {oem} {config_extra}'.strip()
    text = pytesseract.image_to_string(img, lang=lang, config=config)
    return text


def _render_pdf_with_pymupdf(pdf_path: str, dpi: int = 200) -> List[Image.Image]:
    """
    Render PDF pages to PIL images using PyMuPDF (pymupdf).
    """
    if not _has_pymupdf:
        raise RuntimeError("PyMuPDF (pymupdf) is not installed. Install with `pip install pymupdf` or install Poppler and use pdf2image.")
    doc = fitz.open(pdf_path)
    images = []
    zoom = dpi / 72.0  # 72 DPI is the default in PDFs
    mat = fitz.Matrix(zoom, zoom)
    for page in doc:
        pix = page.get_pixmap(matrix=mat, alpha=False)
        mode = "RGB"
        img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
        images.append(img)
    return images


def ocr_pdf(pdf_path: Union[str, Path],
            dpi: int = 200,
            lang: str = "eng",
            preprocess: bool = True,
            psm: int = 3,
            oem: int = 3,
            poppler_path: str = None,
            config_extra: str = "") -> Tuple[str, List[str]]:
    """
    Convert a PDF into images (each page) and run OCR on each page.
    Uses pdf2image.convert_from_path if available (requires Poppler),
    otherwise falls back to PyMuPDF rendering.
    Returns a tuple (combined_text, per_page_texts)
    """
    pdf_path = str(pdf_path)
    images = None

    # Try pdf2image first (uses Poppler)
    if _has_pdf2image:
        convert_kwargs = {"dpi": dpi}
        if poppler_path:
            convert_kwargs["poppler_path"] = poppler_path
        try:
            images = convert_from_path(pdf_path, **convert_kwargs)
        except Exception:
            images = None

    # If pdf2image failed or not available, try PyMuPDF
    if images is None:
        images = _render_pdf_with_pymupdf(pdf_path, dpi=dpi)

    per_page_texts = []
    for i, img in enumerate(images):
        txt = ocr_image(img, lang=lang, preprocess=preprocess, psm=psm, oem=oem, config_extra=config_extra)
        per_page_texts.append(txt)

    combined = "\n\n----- PAGE BREAK -----\n\n".join(per_page_texts)
    return combined, per_page_texts


def extract_text(input_path: Union[str, Path],
                 output_path: Union[str, Path] = None,
                 dpi: int = 200,
                 lang: str = "eng",
                 preprocess: bool = True,
                 psm: int = 3,
                 oem: int = 3,
                 poppler_path: str = None,
                 config_extra: str = "") -> str:
    """
    High-level function. Detects whether input is PDF or image(s) and returns text.
    If output_path is provided, writes text to that file.
    """
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input not found: {input_path}")

    if _is_pdf(input_path):
        combined, _ = ocr_pdf(input_path, dpi=dpi, lang=lang,
                              preprocess=preprocess, psm=psm, oem=oem,
                              poppler_path=poppler_path, config_extra=config_extra)
        out_text = combined
    else:
        out_text = ocr_image(str(input_path), lang=lang, preprocess=preprocess, psm=psm, oem=oem, config_extra=config_extra)

    if output_path:
        output_path = Path(output_path)
        output_path.write_text(out_text, encoding="utf-8")
    return out_text


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="OCR for images and PDFs (using Tesseract + pdf2image or PyMuPDF fallback)")
    parser.add_argument("input", help="Input file (image or PDF)")
    parser.add_argument("-o", "--output", help="Output text file (optional). If not provided, prints to stdout.")
    parser.add_argument("--dpi", type=int, default=200, help="DPI for PDF to image conversion (default 200). Increase for higher quality at cost of memory.")
    parser.add_argument("--lang", default="eng", help="Tesseract language(s), e.g. 'eng' or 'eng+fra'")
    parser.add_argument("--no-preprocess", dest="preprocess", action="store_false", help="Disable preprocessing")
    parser.add_argument("--poppler-path", dest="poppler_path", default=None, help="Path to poppler binaries (if needed on Windows)")
    parser.add_argument("--psm", dest="psm", type=int, default=3, help="Tesseract PSM (page segmentation mode)")
    parser.add_argument("--oem", dest="oem", type=int, default=3, help="Tesseract OEM (OCR engine mode)")
    parser.add_argument("--config-extra", dest="config_extra", default="", help="Extra tesseract config flags")
    args = parser.parse_args()

    text = extract_text(args.input, output_path=args.output, dpi=args.dpi, lang=args.lang,
                        preprocess=args.preprocess, psm=args.psm, oem=args.oem,
                        poppler_path=args.poppler_path, config_extra=args.config_extra)
    if not args.output:
        print(text)