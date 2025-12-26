# test_ocr.py
# Enhanced OCR tester: render PDF page → save image → run multiple preprocessing passes → OCR each
# Usage:
#   python test_ocr_enhanced.py sample_data/shanmu_hallticket.pdf --page 1 --dpi 300
#   python test_ocr_enhanced.py sample_data/Signup_UI.png

import argparse
import os
from pathlib import Path
from PIL import Image
import pytesseract
import numpy as np
import cv2

try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None

# If your tesseract is not in PATH, set env var TESSERACT_CMD and uncomment:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def save_pil(img: Image.Image, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out_path))
    print(f"Saved image to {out_path}")

def render_pdf_page_to_pil(pdf_path: Path, page_num: int = 1, dpi: int = 300):
    if fitz is None:
        raise RuntimeError("PyMuPDF (fitz) not installed")
    doc = fitz.open(str(pdf_path))
    if page_num < 1 or page_num > len(doc):
        raise ValueError("page_num out of range")
    page = doc[page_num - 1]
    pix = page.get_pixmap(dpi=dpi)
    mode = "RGBA" if pix.alpha else "RGB"
    img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
    return img

def pil_to_cv(img: Image.Image):
    arr = np.array(img)
    if arr.ndim == 2:
        return arr
    if arr.shape[2] == 4:
        arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2RGB)
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

def cv_to_pil(cv_img):
    cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(cv_img)

def deskew_image(cv_img):
    # Convert to grayscale and threshold
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    coords = np.column_stack(np.where(th == 0))
    if coords.size == 0:
        return cv_img  # nothing to deskew
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    # rotate
    (h, w) = cv_img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(cv_img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

def preprocess_variants(cv_img):
    """Yield (name, pil_image, cv_img) for a few preprocessing methods."""
    variants = []
    # Original
    variants.append(("orig", cv_to_pil(cv_img), cv_img.copy()))
    # Grayscale
    g = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    variants.append(("gray", Image.fromarray(g), cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)))
    # Bilateral denoise then adaptive threshold
    denoise = cv2.bilateralFilter(g, 9, 75, 75)
    adaptive = cv2.adaptiveThreshold(denoise, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY, 31, 10)
    variants.append(("bilateral_adaptive", Image.fromarray(adaptive), cv2.cvtColor(adaptive, cv2.COLOR_GRAY2BGR)))
    # Otsu threshold after blur
    blur = cv2.GaussianBlur(g, (5,5), 0)
    _, otsu = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    variants.append(("otsu", Image.fromarray(otsu), cv2.cvtColor(otsu, cv2.COLOR_GRAY2BGR)))
    # Deskewed + adaptive
    desk = deskew_image(cv_img)
    g2 = cv2.cvtColor(desk, cv2.COLOR_BGR2GRAY)
    den2 = cv2.bilateralFilter(g2, 9, 75, 75)
    adapt2 = cv2.adaptiveThreshold(den2, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 31, 10)
    variants.append(("deskew_bilateral_adaptive", Image.fromarray(adapt2), cv2.cvtColor(adapt2, cv2.COLOR_GRAY2BGR)))
    return variants

def ocr_pil_image(img_pil, config="--psm 6 --oem 3", lang=None):
    args = {"config": config}
    if lang:
        args["lang"] = lang
    try:
        txt = pytesseract.image_to_string(img_pil, **args)
    except Exception as e:
        txt = f"[OCR error: {e}]"
    return txt

def run_all_ocr_runs(input_path: Path, page: int = 1, dpi: int = 300, lang: str = None, save_dir: Path = Path("tmp_ocr_out")):
    save_dir.mkdir(parents=True, exist_ok=True)
    if input_path.suffix.lower() in (".pdf",):
        pil = render_pdf_page_to_pil(input_path, page_num=page, dpi=dpi)
        img_name = save_dir / f"{input_path.stem}_page{page}_dpi{dpi}.png"
        save_pil(pil, img_name)
    else:
        pil = Image.open(str(input_path))
        img_name = save_dir / f"{input_path.stem}.png"
        save_pil(pil, img_name)

    cv_img = pil_to_cv(pil)
    variants = preprocess_variants(cv_img)

    # list of configs to try
    psm_configs = ["--psm 6 --oem 3", "--psm 3 --oem 3", "--psm 11 --oem 3", "--psm 1 --oem 3"]
    results = []
    for vname, pil_img, cvv in variants:
        # save variant for visual inspection too
        var_path = save_dir / f"{input_path.stem}_{vname}.png"
        save_pil(pil_img, var_path)
        for cfg in psm_configs:
            txt = ocr_pil_image(pil_img, config=cfg, lang=lang)
            results.append((vname, cfg, txt[:800]))  # show first 800 chars
            print("="*80)
            print(f"Variant: {vname} | Config: {cfg}")
            print("-"*80)
            print(txt)
            print("\n\n")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str, help="PDF or image file")
    parser.add_argument("--page", type=int, default=1, help="page number for PDFs (1-based)")
    parser.add_argument("--dpi", type=int, default=300, help="render DPI for PDF")
    parser.add_argument("--lang", type=str, default=None, help="tesseract lang (eg 'eng')")
    args = parser.parse_args()

    input_path = Path(args.file)
    if not input_path.exists():
        print("File not found:", args.file)
        raise SystemExit(1)

    run_all_ocr_runs(input_path, page=args.page, dpi=args.dpi, lang=args.lang)