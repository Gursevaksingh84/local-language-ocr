# ocr_engine.py — OCR engine optimised for Gurmukhi Granth text
#
# Key improvements over original:
#  1. PSM 6 (uniform text block) kept as default — works best for book pages.
#     PSM 4 offered as alternative for single-column layouts.
#  2. OEM 3 (LSTM + legacy combined) for maximum Gurmukhi accuracy.
#  3. preserve_interword_spaces=1 — critical for correct word segmentation.
#  4. gurmukhi_postprocess() — multi-stage Unicode + artifact cleanup:
#       • NFC normalization (fixes decomposed subjoined consonants)
#       • Remove _ ` and stray ASCII from Gurmukhi lines
#       • Remove trailing noise digits (1, l, I) at end of lines
#       • Normalise danda/double-danda variants
#  5. extract_with_confidence() returns per-word confidence scores (pandas).
#  6. Cross-platform Tesseract path setup (Windows registry vs Linux).

import os
import platform
import re
import unicodedata

import pytesseract
from PIL import Image

# ── Tesseract path setup ───────────────────────────────────────────────────────

def _configure_tesseract():
    system = platform.system()
    if system == "Windows":
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r"SOFTWARE\Tesseract-OCR")
            path, _ = winreg.QueryValueEx(key, "InstallDir")
            exe = os.path.join(path, "tesseract.exe")
            if os.path.exists(exe):
                pytesseract.pytesseract.tesseract_cmd = exe
        except Exception:
            pass
    else:
        # Linux/macOS/cloud
        for candidate in ["/usr/bin/tesseract", "/usr/local/bin/tesseract"]:
            if os.path.exists(candidate):
                pytesseract.pytesseract.tesseract_cmd = candidate
                break

_configure_tesseract()


# ── Language map ───────────────────────────────────────────────────────────────

LANGUAGE_MAP = {
    "Punjabi (Gurmukhi)": "pan",
    "Punjabi":            "pan",
    "Hindi":              "hin",
    "Marathi":            "mar",
    "Tamil":              "tam",
    "Telugu":             "tel",
    "Bengali":            "ben",
    "Kannada":            "kan",
    "Malayalam":          "mal",
    "Gujarati":           "guj",
    "English":            "eng",
}

# Languages that benefit from Gurmukhi-specific post-processing
GURMUKHI_LANGS = {"pan", "Punjabi", "Punjabi (Gurmukhi)"}


# ── Post-processing ────────────────────────────────────────────────────────────

def gurmukhi_postprocess(text: str) -> str:
    """
    Multi-stage post-processing for Gurmukhi OCR output.

    Fixes:
    - Decomposed Unicode subjoined consonants (NFC normalization)
    - Underscore artifacts: _ਕਾਨਨ → ਕਾਨਨ
    - Backtick artifacts: ਸੁ`ਐਸੇ → ਸੁਐਸੇ
    - Trailing noise at end of Gurmukhi lines: "ਧੁੰਦ    1" → "ਧੁੰਦ"
    - Double-pipe to double-danda: "||" → "॥"
    - Collapse multiple spaces to single space
    """

    # 1. Unicode NFC normalization
    #    Fixes decomposed subjoined consonants that Tesseract sometimes outputs
    #    as separate code points instead of precomposed sequences.
    text = unicodedata.normalize('NFC', text)

    # 2. Remove underscore artifacts at word boundaries within Gurmukhi text
    #    Pattern: underscore immediately before or after a Gurmukhi character
    GUR = r'[\u0A00-\u0A7F]'
    text = re.sub(rf'_(?={GUR})', '', text)
    text = re.sub(rf'(?<={GUR})_', '', text)
    # Also catch underscore at line start (indentation artifact)
    text = re.sub(r'^\s*_+', '', text, flags=re.MULTILINE)

    # 3. Remove backtick artifacts inside Gurmukhi words
    text = re.sub(rf'(?<={GUR})`(?={GUR})', '', text)

    # 4. Remove trailing ASCII noise digits/chars at end of Gurmukhi lines
    #    e.g. "ਧੁੰਦ    1" or "ਧੁੰਦ r" at line end
    text = re.sub(rf'({GUR}[\u0A00-\u0A7F\s]*?)\s+[1IlLr|]\s*$',
                  r'\1', text, flags=re.MULTILINE)

    # 5. Normalise danda/double-danda variants
    text = text.replace('||', '॥')
    text = text.replace('!!', '॥')

    # 6. Collapse multiple whitespace to single space (but preserve newlines)
    text = re.sub(r'[ \t]{2,}', ' ', text)

    # 7. Remove lines that contain NO Gurmukhi characters and consist only of
    #    ASCII punctuation/noise (e.g. "___-" or "   ---  " from column separators)
    text = re.sub(
        r'^\s*[^\u0A00-\u0A7F\n]*[_\-/]{2,}[^\u0A00-\u0A7F\n]*\s*$',
        '', text, flags=re.MULTILINE
    )

    # 8. Remove completely empty lines (more than 1 blank line → 1 blank line)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


# ── Core OCR ───────────────────────────────────────────────────────────────────

def extract_text(
    image: Image.Image,
    language: str = "Punjabi",
    psm: int = 6,
) -> str:
    """
    Extract text from a preprocessed PIL Image using Tesseract.

    Args:
        image:    Preprocessed (binarised) PIL Image.
        language: Human-readable language name (see LANGUAGE_MAP).
        psm:      Tesseract page segmentation mode.
                  6 = uniform block of text (default, best for Granth pages)
                  4 = single column of variable-size text
                  3 = fully automatic (use for complex mixed layouts)

    Returns:
        Cleaned extracted text string.
    """
    lang_code = LANGUAGE_MAP.get(language, "pan")

    # OEM 3 = combined LSTM + legacy (most accurate for Gurmukhi)
    # preserve_interword_spaces=1 = critical for correct Gurmukhi word spacing
    config = f"--oem 3 --psm {psm} -c preserve_interword_spaces=1"

    raw_text = pytesseract.image_to_string(image, lang=lang_code, config=config)

    # Apply Gurmukhi-specific post-processing when relevant
    if lang_code in {"pan"} or language in GURMUKHI_LANGS:
        return gurmukhi_postprocess(raw_text)

    return raw_text.strip()


def extract_with_confidence(
    image: Image.Image,
    language: str = "Punjabi",
    psm: int = 6,
    min_confidence: int = 0,
):
    """
    Extract text with per-word confidence scores.

    Returns:
        pandas DataFrame with columns: text, conf, left, top, width, height
        Only rows with conf >= min_confidence and non-empty text are returned.
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("pandas is required for extract_with_confidence(). "
                          "Install with: pip install pandas")

    lang_code = LANGUAGE_MAP.get(language, "pan")
    config = f"--oem 3 --psm {psm} -c preserve_interword_spaces=1"

    data = pytesseract.image_to_data(
        image, lang=lang_code, config=config,
        output_type=pytesseract.Output.DATAFRAME
    )

    # Filter out empty/noise rows
    data = data[data["text"].notna()]
    data = data[data["text"].str.strip() != ""]
    data["conf"] = pd.to_numeric(data["conf"], errors="coerce").fillna(0)
    data = data[data["conf"] >= min_confidence]

    return data[["text", "conf", "left", "top", "width", "height"]].reset_index(drop=True)


def get_available_languages() -> list[str]:
    """Return list of supported language names."""
    return list(LANGUAGE_MAP.keys())


# ── CLI test ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    from preprocessor import preprocess_for_gurmukhi

    path = sys.argv[1] if len(sys.argv) > 1 else "test.jpg"
    lang = sys.argv[2] if len(sys.argv) > 2 else "Punjabi"

    print(f"Processing: {path}  |  Language: {lang}")
    img = preprocess_for_gurmukhi(path)
    text = extract_text(img, language=lang)
    print("\n── Extracted Text ──────────────────────────────")
    print(text)
    print("────────────────────────────────────────────────")