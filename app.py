# app.py
# Updated with PDF support

import streamlit as st
from PIL import Image
from preprocessor import preprocess
from ocr_engine import extract_text
from translator import translate_text
from pdf_handler import pdf_to_images, get_pdf_page_count
import tempfile
import os

# ── Page config ────────────────────────────────────────
st.set_page_config(
    page_title="Indian Language OCR Tool",
    page_icon="🌏",
    layout="wide"
)

st.title("🌏 Indian Language OCR & Translator")
st.markdown("Extract and translate text from Indian language images and PDFs")
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
    st.markdown("### 📖 Supported Formats")
    st.markdown("✅ JPG / JPEG\n\n✅ PNG\n\n✅ PDF (multi-page)")

# ── File Upload — now accepts PDF too ──────────────────
uploaded_file = st.file_uploader(
    "Upload an image or PDF",
    type=["jpg", "jpeg", "png", "pdf"],
    help="Upload any image or PDF containing Indian language text"
)

if uploaded_file is not None:

    file_type = uploaded_file.name.split(".")[-1].lower()
    is_pdf = file_type == "pdf"

    # ── PDF handling ───────────────────────────────────
    if is_pdf:
        st.info(f"📄 PDF uploaded: **{uploaded_file.name}**")

        pdf_bytes = uploaded_file.read()

        # Count pages instantly using pypdf
        with st.spinner("Reading PDF..."):
            from pdf_handler import get_pdf_page_count
            total_pages = get_pdf_page_count(pdf_bytes)

        if total_pages:
            st.markdown(f"**Total pages found: {total_pages}**")
        else:
            st.markdown("**Page count unavailable — enter range manually**")
            total_pages = 999

        # Page range selector
        col_a, col_b = st.columns(2)
        with col_a:
            start_page = st.number_input(
                "From page", min_value=1,
                max_value=total_pages, value=1
            )
        with col_b:
            end_page = st.number_input(
                "To page", min_value=1,
                max_value=total_pages, value=min(3, total_pages)
            )

        # Warn if too many pages selected
        pages_selected = end_page - start_page + 1
        if pages_selected > 10:
            st.warning(
                f"⚠️ You selected {pages_selected} pages. "
                "Processing more than 10 pages may be slow. "
                "Consider processing in smaller batches."
            )

        if st.button("🔍 Extract & Translate PDF", type="primary"):

            with st.spinner("Converting PDF pages to images..."):
                from pdf_handler import pdf_to_images
                pages = pdf_to_images(
                    pdf_bytes=pdf_bytes,
                    start_page=int(start_page),
                    end_page=int(end_page)
                )

            if not pages:
                st.error("❌ Could not convert PDF. Check if file is corrupted.")
            else:
                all_extracted = []
                all_translated = []

                progress = st.progress(0)
                status = st.empty()

                for i, page_img in enumerate(pages):
                    status.text(
                        f"Processing page "
                        f"{start_page + i}/{end_page}..."
                    )

                    import tempfile, os
                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=".jpg"
                    ) as tmp:
                        page_img.save(tmp.name, "JPEG")
                        tmp_path = tmp.name

                    cleaned = preprocess(tmp_path)
                    extracted = extract_text(cleaned, ocr_language)
                    translated = translate_text(extracted, target_language)

                    all_extracted.append(
                        f"--- Page {int(start_page) + i} ---\n{extracted}"
                    )
                    all_translated.append(
                        f"--- Page {int(start_page) + i} ---\n{translated}"
                    )

                    os.unlink(tmp_path)
                    progress.progress((i + 1) / len(pages))

                status.text("✅ All pages processed!")

                # Results
                st.divider()
                col1, col2 = st.columns(2)
                full_extracted = "\n\n".join(all_extracted)
                full_translated = "\n\n".join(all_translated)

                with col1:
                    st.subheader(f"📝 Extracted ({ocr_language})")
                    st.text_area("", full_extracted, height=400)

                with col2:
                    st.subheader(f"🌐 Translated ({target_language})")
                    st.text_area("", full_translated, height=400)

                # Metrics
                st.divider()
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric("Pages Processed", len(pages))
                with m2:
                    st.metric("Words Extracted", len(full_extracted.split()))
                with m3:
                    st.metric("Characters", len(full_extracted))

                # Download
                output = f"EXTRACTED ({ocr_language}):\n{full_extracted}\n\nTRANSLATED ({target_language}):\n{full_translated}"
                st.download_button(
                    "📥 Download Results as TXT",
                    data=output,
                    file_name="ocr_results.txt",
                    mime="text/plain",
                    key="pdf_download"
                )

    # ── Image handling ─────────────────────────────────
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📷 Original Image")
            image = Image.open(uploaded_file)
            st.image(image, use_column_width=True)
            st.caption(f"Size: {image.width} x {image.height} px")

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".jpg"
        ) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        if st.button("🔍 Extract & Translate", type="primary", key="img_btn"):

            with st.spinner("Processing..."):
                cleaned = preprocess(tmp_path)

                if show_preprocessed:
                    with col1:
                        st.subheader("🔧 Preprocessed")
                        st.image(cleaned, use_column_width=True)

                extracted = extract_text(cleaned, ocr_language)
                translated = translate_text(extracted, target_language)

            with col2:
                st.subheader("📝 Extracted Text")
                st.text_area(
                    f"Text in {ocr_language}",
                    extracted, height=250
                )
                st.subheader("🌐 Translated Text")
                st.text_area(
                    f"Translation in {target_language}",
                    translated, height=250
                )

            st.divider()
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Words", len(extracted.split()))
            with m2:
                st.metric("Characters", len(extracted))
            with m3:
                st.metric("Lines", len(extracted.splitlines()))

            output = f"EXTRACTED ({ocr_language}):\n{extracted}\n\nTRANSLATED ({target_language}):\n{translated}"
            st.download_button(
                "📥 Download Results as TXT",
                data=output,
                file_name="ocr_results.txt",
                mime="text/plain",
                key="img_download"
            )

        os.unlink(tmp_path)

# ── Footer ─────────────────────────────────────────────
st.divider()
st.markdown("Built with Python • Tesseract OCR • Google Translate • Streamlit")