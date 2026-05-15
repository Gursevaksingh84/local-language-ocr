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
    # --- Step 2: Sharpness check on ORIGINAL image (BEFORE upscaling) ---
    # CRITICAL: sharpness must be measured now. After Lanczos upscaling,
    # Laplacian variance drops ~25x due to interpolation smoothing, making
    # a sharp scan falsely appear blurry and triggering the wrong binarizer.
    gray_orig = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    lap_var = cv2.Laplacian(gray_orig, cv2.CV_64F).var()

    # --- Step 3: Smart upscale only when genuinely low DPI ---
    est_dpi = estimate_dpi(w)
    if est_dpi < 80:
        # Very low DPI (camera photo from distance): upscale to ~285 DPI
        scale = min(285.0 / est_dpi, 3.5)
        img_cv = cv2.resize(img_cv, (int(w * scale), int(h * scale)),
                            interpolation=cv2.INTER_LANCZOS4)
    elif est_dpi < 150:
        # Low-to-moderate DPI (scanned book page ~95–150 DPI): 3x upscale.
        # Scanned granth pages at this range need 3x to resolve subscript consonants.
        img_cv = cv2.resize(img_cv, (int(w * 3.0), int(h * 3.0)),
                            interpolation=cv2.INTER_LANCZOS4)
    # else: ≥ 150 DPI equivalent (clean screenshot etc.) → no upscaling needed

    # --- Step 4: Grayscale ---
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

    # --- Step 5: CLAHE — fixes yellowed book paper and uneven scan illumination ---
    # clipLimit=1.5 is conservative; preserves fine Gurmukhi strokes and subscripts
    clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # --- Step 6: Sharpness-adaptive binarization ---
    # Uses lap_var measured in Step 2 (original image — reliable)
    if lap_var >= 400:
        # Sharp/clean image: mild denoise + Otsu — preserves thin subjoined strokes
        denoised = cv2.fastNlMeansDenoising(gray, h=5, templateWindowSize=7,
                                             searchWindowSize=21)
        _, binary = cv2.threshold(denoised, 0, 255,
                                  cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    else:
        # Blurry/noisy (camera photo, truly old scan): stronger denoise + adaptive threshold
        denoised = cv2.fastNlMeansDenoising(gray, h=9, templateWindowSize=7,
                                             searchWindowSize=21)
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