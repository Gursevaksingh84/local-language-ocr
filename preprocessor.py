# preprocessor.py — Smart image preprocessing for Gurmukhi Granth OCR
#
# Key design decisions for Gurmukhi/Indian script accuracy:
#  1. Smart DPI estimation: only upscale genuinely low-DPI images (< 200 DPI equiv.)
#     Aggressive upscaling of clean screenshots DEGRADES quality.
#  2. CLAHE to fix yellowed/uneven scan illumination — common in old Granth prints.
#  3. Sharpness-adaptive pipeline:
#     - Sharp/clear (Laplacian var > 400): mild denoise + Otsu binarization
#     - Blurry/camera photo (< 400): stronger denoise + adaptive threshold
#  4. NO over-sharpening: Gurmukhi sikhaa (ਸਿਖਾ, the top horizontal bar) and
#     subscript/subjoined consonants (੍ਰ ੍ਵ ੍ਹ) are destroyed by aggressive kernels.
#  5. Lanczos4 interpolation when upscaling: sharpest of all resize methods.

import cv2
import numpy as np
from PIL import Image


def estimate_dpi(image_width_px: int, typical_text_width_inches: float = 5.5) -> float:
    """
    Estimate effective DPI of a scanned book page.
    A standard book text block is roughly 5.5 inches wide.
    """
    return image_width_px / typical_text_width_inches


def preprocess_for_gurmukhi(image_input) -> Image.Image:
    """
    Main preprocessing pipeline optimised for Gurmukhi Granth scans.

    Args:
        image_input: file path (str) or PIL Image or numpy ndarray

    Returns:
        Binarised PIL Image ready for pytesseract
    """
    # --- Load image ---
    if isinstance(image_input, str):
        img_cv = cv2.imread(image_input)
        if img_cv is None:
            raise FileNotFoundError(f"Cannot read image: {image_input}")
    elif isinstance(image_input, Image.Image):
        img_cv = cv2.cvtColor(np.array(image_input.convert("RGB")), cv2.COLOR_RGB2BGR)
    elif isinstance(image_input, np.ndarray):
        img_cv = image_input.copy()
    else:
        raise TypeError(f"Unsupported input type: {type(image_input)}")

    h, w = img_cv.shape[:2]

    # --- Step 1: Smart upscale only when genuinely low DPI ---
    # IMPORTANT: Only upscale camera/scan photos with truly low pixel density.
    # Upscaling clean screenshots or decent scans (≥ 100 DPI effective) DEGRADES
    # Gurmukhi OCR by introducing interpolation blur on thin subjoined glyphs.
    #
    # Thresholds (conservative — when in doubt, don't upscale):
    #   < 80 DPI  → strong upscale needed (camera photo of book from far away)
    #   80–100    → gentle 1.5x upscale
    #   > 100     → no upscaling; image is fine for Tesseract as-is
    est_dpi = estimate_dpi(w)
    if est_dpi < 80:
        # Very low DPI (e.g. camera photo from distance): upscale to ~240 DPI
        scale = min(240.0 / est_dpi, 3.0)
        new_w = int(w * scale)
        new_h = int(h * scale)
        img_cv = cv2.resize(img_cv, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
    elif est_dpi < 100:
        # Marginally low DPI: gentle 1.5x upscale
        img_cv = cv2.resize(img_cv, (int(w * 1.5), int(h * 1.5)), interpolation=cv2.INTER_LANCZOS4)
    # else: ≥ 100 DPI equivalent → no upscaling; Tesseract handles it well

    # --- Step 2: Grayscale ---
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

    # --- Step 3: CLAHE — fixes yellowed book paper and uneven scan illumination ---
    # clipLimit=2.0 is conservative; higher values over-contrast and break thin strokes
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # --- Step 4: Sharpness-adaptive binarization ---
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()

    if lap_var >= 400:
        # Sharp/clean image (screenshot, clean scan): mild denoise + Otsu
        # h=5 is very light — preserves thin Gurmukhi strokes
        denoised = cv2.fastNlMeansDenoising(gray, h=5, templateWindowSize=7, searchWindowSize=21)
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    else:
        # Blurry/noisy (camera photo, old scan): stronger denoise + adaptive threshold
        # h=9 removes noise while adaptive threshold handles uneven illumination
        denoised = cv2.fastNlMeansDenoising(gray, h=9, templateWindowSize=7, searchWindowSize=21)
        # blockSize=19, C=8: tuned for Gurmukhi text at ~200+ DPI
        binary = cv2.adaptiveThreshold(
            denoised, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            19, 8
        )

    return Image.fromarray(binary)


# ── Backward-compatible wrapper for existing app.py calls ──────────────────────

def preprocess_image(image_path: str) -> Image.Image:
    """
    Drop-in replacement for the original preprocess_image() function.
    Now uses the Gurmukhi-optimised pipeline internally.
    """
    return preprocess_for_gurmukhi(image_path)


def get_image_quality_score(image_path: str) -> float:
    """
    Returns Laplacian variance (sharpness score).
    > 400  → clean/sharp
    100–400 → moderate
    < 100  → blurry
    """
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return 0.0
    return float(cv2.Laplacian(img, cv2.CV_64F).var())


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "test.jpg"
    score = get_image_quality_score(path)
    print(f"Quality score: {score:.1f} ({'sharp' if score > 400 else 'blurry'})")
    out = preprocess_for_gurmukhi(path)
    out.save("preprocessed_output.png")
    print("Saved: preprocessed_output.png")