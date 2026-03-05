# 🌏 Local Language OCR & Translator

> Extract and translate text from Indian regional language images and PDFs — built with Python, Tesseract OCR, and Streamlit.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red?logo=streamlit)
![Tesseract](https://img.shields.io/badge/Tesseract_OCR-5.x-green)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8-blue?logo=opencv)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📸 Demo

> Upload a Hindi newspaper, Punjabi scripture, Tamil document — get extracted text and English translation instantly.

| Upload Image/PDF | Extract Text | Translate |
|---|---|---|
| JPG, PNG, PDF | Tesseract OCR | Google Translate |

---

## ✨ Features

- 📷 **Image Support** — Upload JPG, PNG images containing Indian language text
- 📄 **PDF Support** — Multi-page PDF processing with page range selection
- 🔤 **9 Indian Languages** — Hindi, Tamil, Telugu, Bengali, Kannada, Malayalam, Marathi, Gujarati, Punjabi
- 🌐 **Translation** — Translate extracted text to English, Hindi, Punjabi, Tamil, Telugu, French, Spanish
- 🧠 **Smart Preprocessing** — Auto-detects image quality and applies light or heavy preprocessing accordingly
- 📊 **Confidence Scoring** — Word-level OCR confidence analysis
- 📥 **Download Results** — Save extracted + translated text as TXT file
- 📈 **Live Metrics** — Word count, character count, lines extracted

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.11 | Core language |
| Tesseract OCR 5.x | Text extraction engine |
| OpenCV | Image preprocessing (denoise, threshold, sharpen) |
| Pillow (PIL) | Image loading and conversion |
| Google Translate API | Text translation |
| Streamlit | Web application UI |
| pdf2image + Poppler | PDF to image conversion |
| pypdf | PDF page counting |
| langdetect | Language auto-detection |
| pandas | Data handling and CSV export |

---

## 🌐 Supported Languages

| Language | Script | Tesseract Code |
|---|---|---|
| Hindi | Devanagari | `hin` |
| Punjabi | Gurmukhi | `pan` |
| Tamil | Tamil | `tam` |
| Telugu | Telugu | `tel` |
| Bengali | Bengali | `ben` |
| Kannada | Kannada | `kan` |
| Malayalam | Malayalam | `mal` |
| Marathi | Devanagari | `mar` |
| Gujarati | Gujarati | `guj` |

---

## ⚙️ How It Works

```
📁 Input (Image or PDF)
        ↓
🔧 Preprocessing (OpenCV)
   • Auto quality detection (Laplacian variance)
   • Grayscale conversion
   • Noise removal
   • Adaptive thresholding
   • Sharpening
        ↓
🔤 OCR Extraction (Tesseract)
   • Language-specific model
   • LSTM neural network (OEM 3)
   • Page segmentation (PSM 6)
        ↓
🌐 Translation (Google Translate)
   • Extracted text → target language
        ↓
📊 Results + Download
```

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.11+
- Tesseract OCR 5.x
- Poppler (for PDF support)

---

### 1. Clone the Repository

```bash
git clone https://github.com/Gursevaksingh84/local-language-ocr.git
cd local-language-ocr
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Tesseract OCR (Windows)

Download from 👉 [UB Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

During installation, select these language packs:
```
☑ Hindi  ☑ Tamil  ☑ Telugu  ☑ Bengali
☑ Kannada  ☑ Malayalam  ☑ Marathi  ☑ Gujarati  ☑ Punjabi
```

Then update the path in `ocr_engine.py`:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### 5. Install Poppler (Windows — for PDF support)

Download from 👉 [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases)

Extract and add the `bin` folder to your system PATH.

### 6. Run the App

```bash
streamlit run app.py
```

Open your browser at 👉 `http://localhost:8501`

---

## 📁 Project Structure

```
local-language-ocr/
│
├── app.py              # Streamlit web application
├── preprocessor.py     # Image preprocessing pipeline (OpenCV)
├── ocr_engine.py       # Tesseract OCR text extraction
├── translator.py       # Google Translate integration
├── pdf_handler.py      # PDF to image conversion
│
├── requirements.txt    # Python dependencies
├── packages.txt        # System dependencies (for deployment)
│
├── test_image.jpeg     # Sample test image
└── README.md           # This file
```

---

## 📦 requirements.txt

```
streamlit==1.28.0
pytesseract==0.3.10
Pillow==10.0.0
opencv-python-headless==4.8.0.76
googletrans==4.0.0rc1
langdetect==1.0.9
pandas==2.0.3
numpy==1.24.0
pdf2image==1.16.3
pypdf==3.17.0
```

---

## 🧠 Key Technical Decisions

**Why Tesseract over AWS Textract?**
Tesseract is the only production-grade open-source OCR engine with official support for all major Indian language scripts. AWS Textract doesn't support most Indian languages.

**Why Smart Preprocessing?**
Clean screenshots and camera photos need different preprocessing. We use Laplacian variance to detect image quality and automatically choose between light (Otsu threshold) and heavy (adaptive threshold + denoise + sharpen) pipelines — improving accuracy significantly.

**Why pdf2image + pypdf together?**
pypdf reads PDF metadata (page count) instantly without rendering. pdf2image handles the actual page-to-image conversion with `first_page`/`last_page` parameters so we never load a full PDF into memory at once.

---

## 🔮 Future Enhancements

- [ ] Fine-tune custom Tesseract model on Indian language dataset
- [ ] Android app using ML Kit for on-device OCR
- [ ] Text-to-speech output in original language (gTTS)
- [ ] REST API backend using FastAPI
- [ ] Handwritten text recognition using Vision Transformer
- [ ] Batch processing with CSV export for multiple files

---

## 🙋 About

This project was inspired by a real need: millions of Indian documents exist only in regional language print, making them inaccessible to people who don't read those scripts. This tool aims to bridge that gap.

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

⭐ If this project helped you, please give it a star on GitHub!