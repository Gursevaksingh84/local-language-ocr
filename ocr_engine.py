# ocr_engine.py — Tesseract OCR engine

import pytesseract
from PIL import Image
import os

# ── Tesseract path: works on both Windows and Streamlit Cloud (Linux) ──
if os.name == "nt":
    # Windows (your local machine)
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
else:
    # Linux / Streamlit Cloud — tesseract is on PATH after packages.txt install
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

LANGUAGES = {
    "Hindi":     "hin",
    "Punjabi":   "pan",
    "Tamil":     "tam",
    "Telugu":    "tel",
    "Bengali":   "ben",
    "Kannada":   "kan",
    "Malayalam": "mal",
    "Marathi":   "mar",
    "Gujarati":  "guj",
    "English":   "eng",
}

def extract_text(image, language: str = "Hindi") -> str:
    """Extract text from a PIL Image using Tesseract OCR."""
    lang_code = LANGUAGES.get(language, "hin")
    config = "--oem 3 --psm 6 -c preserve_interword_spaces=1"
    try:
        text = pytesseract.image_to_string(
            image,
            lang=lang_code,
            config=config
        )
        return text.strip()
    except Exception as e:
        return f"[OCR error: {e}]"


def extract_text_from_path(image_path: str, language: str = "Hindi") -> str:
    """Extract text from an image file path."""
    image = Image.open(image_path)
    return extract_text(image, language)


def extract_with_confidence(image, language: str = "Hindi") -> dict:
    """Extract text with per-word confidence scores."""
    lang_code = LANGUAGES.get(language, "hin")
    config = "--oem 3 --psm 6"
    try:
        import pandas as pd
        data = pytesseract.image_to_data(
            image, lang=lang_code, config=config,
            output_type=pytesseract.Output.DICT
        )
        df = pd.DataFrame(data)
        df = df[df["conf"] > 0]
        avg_conf = df["conf"].mean() if not df.empty else 0
        text = " ".join(df["text"].dropna().tolist())
        return {"text": text, "confidence": round(avg_conf, 1)}
    except Exception as e:
        return {"text": f"[Error: {e}]", "confidence": 0}


if __name__ == "__main__":
    print("Tesseract path:", pytesseract.pytesseract.tesseract_cmd)
    print("Available languages:", pytesseract.get_languages())