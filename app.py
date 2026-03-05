import streamlit as st
from PIL import Image
from preprocessor import preprocess
from ocr_engine import extract_text, extract_text_from_path
from translator import translate_text, full_pipeline
import tempfile
import os

# ── Page config — must be FIRST streamlit command ──────
st.set_page_config(
    page_title="Indian Language OCR Tool",
    page_icon="🌏",
    layout="wide"
)

# ── App title ──────────────────────────────────────────
st.title("🌏 Indian Language OCR & Translator")
st.markdown("Extract and translate text from Indian language images")
st.divider()

# ── Sidebar ────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")

    ocr_language = st.selectbox(
        "Source Language (in image)",
        ["Hindi", "Tamil", "Telugu", "Bengali",
         "Kannada", "Malayalam", "Marathi",
         "Gujarati", "Punjabi", "English"]
    )

    target_language = st.selectbox(
        "Translate To",
        ["English", "Hindi", "Punjabi",
         "Tamil", "Telugu", "French", "Spanish"]
    )

    show_preprocessed = st.checkbox(
        "Show preprocessed image", value=False
    )

    st.divider()
    st.markdown("### 📖 About")
    st.markdown(
        "This tool extracts text from images "
        "in Indian regional languages and "
        "translates it to your chosen language."
    )
# ── Main area ──────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Upload an image",
    type=["jpg", "jpeg", "png"],
    help="Upload any image containing Indian language text"
)

if uploaded_file is not None:

    # Show original image
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📷 Original Image")
        image = Image.open(uploaded_file)
        st.image(image, use_column_width=True)
        st.caption(f"Size: {image.width} x {image.height} pixels")

    # Save uploaded file temporarily so OpenCV can read it
    # (OpenCV needs a file path, not a file object)
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=".jpg"
    ) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name
# ── Process button ─────────────────────────────────
    if st.button("🔍 Extract & Translate", type="primary"):

        with st.spinner("Processing... this may take a few seconds"):

            # Preprocess
            cleaned = preprocess(tmp_path)

            # Show preprocessed if checkbox is on
            if show_preprocessed:
                with col1:
                    st.subheader("🔧 Preprocessed Image")
                    st.image(cleaned, use_column_width=True)

            # OCR
            extracted = extract_text(cleaned, ocr_language)

            # Translate
            translated = translate_text(extracted, target_language)

        # ── Show results ───────────────────────────────
        with col2:
            st.subheader("📝 Extracted Text")
            st.text_area(
                f"Text in {ocr_language}",
                extracted,
                height=250
            )

            st.subheader("🌐 Translated Text")
            st.text_area(
                f"Translation in {target_language}",
                translated,
                height=250
            )

        # ── Metrics row ────────────────────────────────
        st.divider()
        m1, m2, m3 = st.columns(3)
        with m1:
            word_count = len(extracted.split())
            st.metric("Words Extracted", word_count)
        with m2:
            char_count = len(extracted)
            st.metric("Characters", char_count)
        with m3:
            line_count = len(extracted.splitlines())
            st.metric("Lines", line_count)

        # ── Download button ────────────────────────────
        st.divider()
        output = f"EXTRACTED ({ocr_language}):\n{extracted}\n\nTRANSLATED ({target_language}):\n{translated}"

        st.download_button(
            label="📥 Download Results as TXT",
            data=output,
            file_name="ocr_results.txt",
            mime="text/plain"
        )

    # Cleanup temp file
    os.unlink(tmp_path)
# ── Footer ─────────────────────────────────────────────
st.divider()
st.markdown(
    "Built with Python • Tesseract OCR • "
    "Google Translate • Streamlit"
)    