# add these imports near top of src/ingest.py if not present
import cv2
import numpy as np

# Replace existing _ocr_image with this function:
def _ocr_image(img: "Image.Image", psm_options=None, debug_save_dir: str = None) -> str:
    """
    Enhanced OCR: generate preprocessing variants, optionally crop likely table area,
    run Tesseract with a list of psm configs, score each OCR output for relevance,
    and return the best OCR text.

    - img: PIL Image
    - psm_options: list of tesseract config strings (e.g., ["--psm 6 --oem 3", "--psm 3 --oem 3"])
      if None, a default list is used.
    - debug_save_dir: if provided, saves variant images to this folder for inspection.
    """
    if Image is None or pytesseract is None:
        return ""

    # configure tesseract binary if env var set
    _configure_tesseract()

    # default PSM configs to try
    if psm_options is None:
        psm_options = ["--psm 6 --oem 3", "--psm 3 --oem 3", "--psm 11 --oem 3", "--psm 1 --oem 3"]

    # helper: convert PIL -> OpenCV BGR
    def pil_to_cv(pil_img):
        arr = np.array(pil_img)
        if arr.ndim == 2:
            return cv2.cvtColor(arr, cv2.COLOR_GRAY2BGR)
        if arr.shape[2] == 4:
            arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2RGB)
        return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

    # helper: convert cv -> pil
    def cv_to_pil(cv_img):
        cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        return Image.fromarray(cv_img)

    # simple deskew using image moments / minAreaRect
    def deskew(cv_img):
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        coords = np.column_stack(np.where(th == 0))
        if coords.size == 0:
            return cv_img
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = cv_img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(cv_img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated

    # preprocess variants: returns list of (name, pil_img, cv_img)
    def build_variants(base_pil):
        cv_base = pil_to_cv(base_pil)
        variants = []
        # original
        variants.append(("orig", base_pil, cv_base.copy()))
        # grayscale (pil)
        gray = cv2.cvtColor(cv_base, cv2.COLOR_BGR2GRAY)
        variants.append(("gray", Image.fromarray(gray), cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)))
        # bilateral denoise + adaptive threshold
        den = cv2.bilateralFilter(gray, 9, 75, 75)
        adapt = cv2.adaptiveThreshold(den, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10)
        variants.append(("bilateral_adaptive", Image.fromarray(adapt), cv2.cvtColor(adapt, cv2.COLOR_GRAY2BGR)))
        # Otsu after blur
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, otsu = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        variants.append(("otsu", Image.fromarray(otsu), cv2.cvtColor(otsu, cv2.COLOR_GRAY2BGR)))
        # deskew + adaptive
        desk = deskew(cv_base)
        gdesk = cv2.cvtColor(desk, cv2.COLOR_BGR2GRAY)
        den2 = cv2.bilateralFilter(gdesk, 9, 75, 75)
        adapt2 = cv2.adaptiveThreshold(den2, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10)
        variants.append(("deskew_bilateral_adaptive", Image.fromarray(adapt2), cv2.cvtColor(adapt2, cv2.COLOR_GRAY2BGR)))
        return variants

    # helper to score OCRed text for relevancy to "course/table" extraction
    def score_text(txt: str) -> float:
        if not txt:
            return 0.0
        s = txt.lower()
        score = 0.0
        # keyword boosts
        keywords = ["course", "course name", "degree", "branch", "seat number", "register no", "applied", "chemistry", "physics"]
        for k in keywords:
            if k in s:
                score += 2.0
        # uppercase-heavy lines heuristic (table row likelihood)
        lines = [ln.strip() for ln in txt.splitlines() if ln.strip()]
        uppercase_line_count = 0
        for ln in lines:
            alpha = sum(1 for ch in ln if ch.isalpha())
            if alpha == 0:
                continue
            upper = sum(1 for ch in ln if ch.isupper())
            if upper / alpha > 0.6 and len(ln.split()) >= 2:
                uppercase_line_count += 1
        score += min(uppercase_line_count, 5) * 1.0
        # presence of many digits (seat numbers/dates)
        digits = sum(c.isdigit() for c in txt)
        score += min(digits / 50.0, 2.0)
        return score

    # run OCR for variants and psm options, optionally also on bottom-half crop
    base_variants = build_variants(img)
    best_text = ""
    best_score = -1.0
    best_meta = None

    # prepare debug dir if requested
    debug_dir = None
    if debug_save_dir:
        debug_dir = Path(debug_save_dir)
        debug_dir.mkdir(parents=True, exist_ok=True)

    for vname, pil_img, cv_img in base_variants:
        # two passes: full image, and likely-table crop (bottom half)
        candidates = [("full", pil_img, cv_img)]
        # crop bottom half heuristic (useful for halltickets with table in lower half)
        h = cv_img.shape[0]
        w = cv_img.shape[1]
        crop_cv = cv_img[h//2: h, 0: w]
        if crop_cv.size > 0:
            candidates.append(("bottom_half", cv_to_pil(crop_cv), crop_cv))

        for ctag, c_pil, c_cv in candidates:
            # optionally save variant images for debugging
            if debug_dir:
                fname = f"{debug_dir}/{vname}_{ctag}.png"
                c_pil.save(fname)

            for cfg in psm_options:
                try:
                    text = pytesseract.image_to_string(c_pil, config=cfg)
                except Exception as e:
                    text = ""
                s = score_text(text)
                # small boost if keywords appear in first 2 lines (more likely title/header)
                first_two = "\n".join(text.splitlines()[:2]).lower()
                if any(k in first_two for k in ["course", "degree", "branch"]):
                    s += 1.5
                # choose best
                if s > best_score:
                    best_score = s
                    best_text = text
                    best_meta = {"variant": vname, "crop": ctag, "cfg": cfg, "score": s}

    # debug print minimal info
    logger.debug("OCR best_meta: %s", best_meta)
    return best_text