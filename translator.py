from googletrans import Translator, LANGUAGES
from preprocessor import preprocess
from ocr_engine import extract_text
# ── Create translator object ───────────────────────────
translator = Translator()

# ── Supported target languages ─────────────────────────
TARGET_LANGUAGES = {
    "English":  "en",
    "Hindi":    "hi",
    "Tamil":    "ta",
    "Telugu":   "te",
    "Punjabi":  "pa",
    "French":   "fr",
    "Spanish":  "es",
    "German":   "de"
}

def translate_text(text, target_language="English"):
    """
    Takes extracted text and target language name.
    Returns translated text as string.
    """
    # Don't translate empty text
    if not text or text.strip() == "":
        return "No text to translate"

    target_code = TARGET_LANGUAGES.get(target_language, "en")

    try:
        result = translator.translate(text, dest=target_code)
        return result.text

    except Exception as e:
        return f"Translation failed: {str(e)}"


def detect_language(text):
    """
    Auto-detects what language the text is in.
    Returns language name and confidence.
    """
    if not text or text.strip() == "":
        return "Unknown", 0.0

    try:
        detection = translator.detect(text)
        # detection.lang = language code e.g. "hi"
        # detection.confidence = 0.0 to 1.0
        lang_name = LANGUAGES.get(detection.lang, "Unknown")
        confidence = round(detection.confidence * 100, 1)
        return lang_name, confidence

    except Exception as e:
        return "Unknown", 0.0

def full_pipeline(image_path, ocr_language="Hindi", target_language="English"):
    """
    Complete pipeline:
    image path → preprocess → OCR → translate → English text
    """
    print(f"Processing: {image_path}")

    # Step 1: Preprocess
    print("Step 1/3: Preprocessing image...")
    cleaned = preprocess(image_path)

    # Step 2: Extract text
    print("Step 2/3: Extracting text with OCR...")
    extracted = extract_text(cleaned, ocr_language)

    # Step 3: Translate
    print("Step 3/3: Translating...")
    translated = translate_text(extracted, target_language)

    return {
        "extracted":  extracted,
        "translated": translated,
        "language":   ocr_language
    }


# ── Test full pipeline ─────────────────────────────────
if __name__ == "__main__":
    result = full_pipeline("test_image.jpeg", "Hindi", "English")

    print("\n" + "=" * 50)
    print("EXTRACTED HINDI TEXT (first 300 chars):")
    print("=" * 50)
    print(result["extracted"][:300])

    print("\n" + "=" * 50)
    print("TRANSLATED ENGLISH TEXT (first 300 chars):")
    print("=" * 50)
    print(result["translated"][:300])
