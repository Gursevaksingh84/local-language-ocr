# translator.py — uses deep-translator (Python 3.13+ compatible)

from deep_translator import GoogleTranslator

TARGET_LANGUAGES = {
    "English":  "en",
    "Hindi":    "hi",
    "Punjabi":  "pa",
    "Tamil":    "ta",
    "Telugu":   "te",
    "French":   "fr",
    "Spanish":  "es",
    "German":   "de",
}

def translate_text(text: str, target_language: str) -> str:
    """Translate text to the target language."""
    if not text or not text.strip():
        return ""
    lang_code = TARGET_LANGUAGES.get(target_language, "en")
    try:
        # deep-translator handles long text by chunking automatically
        translated = GoogleTranslator(source="auto", target=lang_code).translate(text)
        return translated or text
    except Exception as e:
        return f"[Translation error: {e}]"


def detect_language(text: str) -> str:
    """Detect language of text."""
    try:
        from langdetect import detect
        code = detect(text)
        return code
    except Exception:
        return "unknown"


if __name__ == "__main__":
    sample = "नमस्ते, यह एक परीक्षण है।"
    print("Original:", sample)
    print("English:", translate_text(sample, "English"))
    print("Punjabi:", translate_text(sample, "Punjabi"))