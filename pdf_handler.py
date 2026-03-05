# pdf_handler.py
from pdf2image import convert_from_bytes, convert_from_path
from PIL import Image
import io

# Paste YOUR path from Step 2 here
POPPLER_PATH = r"D:\toc\Release-25.12.0-0\poppler-25.12.0\Library\bin\pdftoppm.exe"

def get_pdf_page_count(pdf_bytes):
    """
    Counts PDF pages instantly using pypdf — no image conversion needed.
    """
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(pdf_bytes))
        count = len(reader.pages)
        print(f"PDF has {count} pages")
        return count
    except Exception as e:
        print(f"Page count error: {str(e)}")
        return 10  # safe default if pypdf fails

def pdf_to_images(pdf_bytes=None, pdf_path=None,
                  start_page=1, end_page=1, dpi=300):
    """
    Converts only selected pages to images.
    Never loads whole PDF at once.
    """
    try:
        if pdf_bytes:
            images = convert_from_bytes(
                pdf_bytes,
                dpi=dpi,
                fmt="jpeg",
                first_page=start_page,
                last_page=end_page
                
            )
        elif pdf_path:
            images = convert_from_path(
                pdf_path,
                dpi=dpi,
                fmt="jpeg",
                first_page=start_page,
                last_page=end_page
            )
        else:
            return []

        print(f"Converted pages {start_page}–{end_page}: {len(images)} image(s)")
        return images

    except Exception as e:
        print(f"PDF conversion error: {str(e)}")
        return []