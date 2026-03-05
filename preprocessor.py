# preprocessor.py
# Module 3 (Improved): Smart preprocessing pipeline

import cv2
import numpy as np
from PIL import Image

def get_image_quality(img_cv):
    """
    Checks how blurry an image is.
    Returns a score — higher = sharper image.
    """
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    # Laplacian variance measures sharpness
    # Sharp image = high variance = high score
    score = cv2.Laplacian(gray, cv2.CV_64F).var()
    return score


def preprocess_light(img_cv):
    """
    Light preprocessing for clean screenshots/scans.
    Just grayscale + mild threshold — don't over-process.
    """
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

    # Simple binary threshold (not adaptive)
    # Works great for clean high-contrast images
    _, thresh = cv2.threshold(
        gray, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    return thresh


def preprocess_heavy(img_cv):
    """
    Heavy preprocessing for noisy photos/camera shots.
    Full pipeline — denoise + adaptive threshold + sharpen.
    """
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

    # Step 1: Denoise
    denoised = cv2.fastNlMeansDenoising(gray, h=10)

    # Step 2: Adaptive threshold
    thresh = cv2.adaptiveThreshold(
        denoised, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )

    # Step 3: Sharpen
    kernel = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
    sharpened = cv2.filter2D(thresh, -1, kernel)

    return sharpened


def preprocess(image_path):
    """
    Smart pipeline — automatically chooses light or heavy
    preprocessing based on image quality score.
    """
    img = cv2.imread(image_path)

    # Check sharpness
    quality_score = get_image_quality(img)
    print(f"Image quality score: {quality_score:.1f}")

    if quality_score > 500:
        # Clean screenshot or scan — use light processing
        print("Clean image detected → using light preprocessing")
        processed = preprocess_light(img)
    else:
        # Blurry/noisy photo — use heavy processing
        print("Noisy image detected → using heavy preprocessing")
        processed = preprocess_heavy(img)

    # Convert to PIL for Tesseract
    final = Image.fromarray(processed)
    return final


# ── Test ───────────────────────────────────────────────
if __name__ == "__main__":
    result = preprocess("test_image.jpeg")
    result.save("preprocessed_final.jpg")
    print("Done! Size:", result.size)
    result.show()