import cv2
import numpy as np
from PIL import Image

def preprocess(image_path):
    """
    Takes an image path, runs full preprocessing pipeline,
    returns a clean PIL Image ready for OCR.
    """
    # Load image
    img = cv2.imread(image_path)

    # Step 1: Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Step 2: Denoise
    denoised = cv2.fastNlMeansDenoising(gray, h=10)

    # Step 3: Adaptive threshold
    thresh = cv2.adaptiveThreshold(
        denoised, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )

    # Step 4: Sharpen
    kernel = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
    sharpened = cv2.filter2D(thresh, -1, kernel)

    # Convert back to PIL Image (Tesseract needs PIL format)
    final = Image.fromarray(sharpened)

    return final


#Test 
if __name__ == "__main__":
    result = preprocess("test_image.jpeg")
    result.save("preprocessed_final.jpg")
    print("Preprocessing complete!")
    print("Output size:", result.size)
    result.show()