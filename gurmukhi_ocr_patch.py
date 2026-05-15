# gurmukhi_ocr_patch.py
# ─────────────────────────────────────────────────────────────────────────────
# Drop-in helper module for app.py.
#
# WHAT THIS FIXES
# ───────────────
# 1. ਪ੍ਰਕਾਸ਼ → ਪਕਾਸ਼ type errors (subscript/subjoined consonant ੍ਰ dropped)
#    Root cause: Tesseract cannot see the tiny ੍ਰ glyph on low-DPI scans.
#    Fix: smart upscaling only when image DPI is genuinely low (< 200 equiv.)
#
# 2. Underscore/backtick artifacts in output (_ਕਾਨਨ, ਸੁ`ਐਸੇ)
#    Root cause: Tesseract confuses text column separators with characters.
#    Fix: regex post-processing in gurmukhi_postprocess().
#
# 3. Trailing noise digits at end of Gurmukhi lines ("ਧੁੰਦ   1")
#    Root cause: Page margin marks or noise read as "1".
#    Fix: regex strips trailing lone ASCII at Gurmukhi line ends.
#
# 4. Decomposed Unicode subjoined consonants
#    Root cause: Tesseract occasionally outputs decomposed Unicode sequences.
#    Fix: unicodedata.normalize('NFC', text)
#
# HOW TO INTEGRATE INTO app.py
# ─────────────────────────────
# Replace the current image OCR block in app.py:
#
#   OLD:
#       processed_image = preprocess_image(tmp_path)
#       extracted_text = extract_text(processed_image, language=selected_language)
#
#   NEW:
#       from gurmukhi_ocr_patch import smart_extract
#       extracted_text = smart_extract(tmp_path, language=selected_language)
#
# That's it. smart_extract() handles everything internally.
# ─────────────────────────────────────────────────────────────────────────────

from preprocessor import preprocess_for_gurmukhi
from ocr_engine import extract_text, gurmukhi_postprocess


def smart_extract(
    image_path: str,
    language: str = "Punjabi",
    psm: int = 6,
) -> str:
    """
    One-call Gurmukhi-optimised OCR.

    Pipeline:
        1. Smart preprocessing (DPI-aware upscale → CLAHE → denoise → binarize)
        2. Tesseract OEM 3, PSM 6 (configurable), preserve_interword_spaces
        3. Gurmukhi post-processing (NFC, artifact removal, danda fix)

    Args:
        image_path: Path to the input image (JPG, PNG, TIFF, etc.)
        language:   One of the LANGUAGE_MAP keys in ocr_engine.py
        psm:        Tesseract PSM mode.
                    6 = uniform text block (best for Granth pages — default)
                    4 = single column, variable text sizes
                    3 = fully automatic (use for complex/mixed layouts)

    Returns:
        Cleaned extracted text string.
    """
    processed = preprocess_for_gurmukhi(image_path)
    return extract_text(processed, language=language, psm=psm)


# ── Gurmukhi OCR tips for the Streamlit UI sidebar ────────────────────────────

GURMUKHI_TIPS = """
### 📖 Gurmukhi Granth OCR Tips

**For best results:**
- **Use clear scans** — 300 DPI or higher. Camera photos reduce accuracy of 
  subjoined consonants like ੍ਰ (subscript Ra) in words like ਪ੍ਰਕਾਸ਼, ਗ੍ਰੰਥ.
- **Avoid shadows and skew** — even mild page curl near the spine causes errors.
- **PDF from scanner** — use the PDF upload mode; each page is rendered at 300 DPI.
- **One page at a time** — multi-column or decorated pages (borders, headings in 
  different scripts) may need PSM 3 (auto) instead of PSM 6.

**Known Tesseract limitations with Gurmukhi:**
- Old-style typefaces (pre-1990 prints) have lower accuracy than modern Unicode fonts.
- Mixed Hindi+Gurmukhi pages: select Hindi or Punjabi based on majority script.
- The `pan` (Punjabi) Tesseract model covers standard Gurmukhi (Suraj Prakash, 
  Guru Granth Sahib, modern Punjabi) well. Rare archaic ligatures may still error.
"""


def add_gurmukhi_sidebar_tips(st):
    """
    Call this in app.py's sidebar section when Punjabi/Gurmukhi is selected.
    Usage:
        if selected_language in ("Punjabi", "Punjabi (Gurmukhi)"):
            from gurmukhi_ocr_patch import add_gurmukhi_sidebar_tips
            add_gurmukhi_sidebar_tips(st)
    """
    st.sidebar.markdown(GURMUKHI_TIPS)