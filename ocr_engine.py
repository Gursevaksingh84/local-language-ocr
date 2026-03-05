import pytesseract
from PIL import Image
from preprocessor import preprocess
import pandas as pd

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

LANGUAGES = {
    "Hindi":     "hin",
    "Tamil":     "tam",
    "Telugu":    "tel",
    "Bengali":   "ben",
    "Kannada":   "kan",
    "Malayalam": "mal",
    "Marathi":   "mar",
    "Gujarati":  "guj",
    "Punjabi":   "pan",   
    "English":   "eng"
}

def extract_text(image, language="Hindi"):
    lang_code = LANGUAGES.get(language, "hin")

    # config tells Tesseract HOW to read the image
    config = "--oem 3 --psm 6"

    text = pytesseract.image_to_string(
        image,
        lang=lang_code,
        config=config
    )
    return text.strip()
def extract_text_from_path(image_path, language="Hindi"):
    """
    Takes an image file path.
    Preprocesses it first, then extracts text.
    """
    cleaned_image = preprocess(image_path)
    text = extract_text(cleaned_image, language)
    return text
def extract_with_confidence(image, language="Hindi"):
    """
    Returns detailed word-by-word OCR data
    including confidence scores for each word.
    """
    lang_code = LANGUAGES.get(language, "hin")
    config = "--oem 3 --psm 6"

    # image_to_data returns a full breakdown
    data = pytesseract.image_to_data(
        image,
        lang=lang_code,
        config=config,
        output_type=pytesseract.Output.DATAFRAME
    )

    # Filter out empty rows and low confidence
    words = data[data["conf"] > 0][["text", "conf"]]
    words = words[words["text"].str.strip() != ""]

    return words
