# app.py — BhashaScan v5 — All bugs fixed

import streamlit as st
from PIL import Image
from preprocessor import preprocess
from ocr_engine import extract_text
from translator import translate_text
from pdf_handler import pdf_to_images, get_pdf_page_count
import tempfile, os, time

st.set_page_config(
    page_title="BhashaScan — Indian Language OCR",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Keep sidebar permanently expanded — re-open it if user collapses it
st.markdown("""
<script>
(function keepSidebarOpen() {
    function forceOpen() {
        const sb = window.parent.document.querySelector('[data-testid="stSidebar"]');
        if (sb && sb.getAttribute('aria-expanded') === 'false') {
            const btn = window.parent.document.querySelector('[data-testid="collapsedControl"] button');
            if (btn) btn.click();
        }
    }
    // Run immediately and keep watching
    setInterval(forceOpen, 300);
})();
</script>
""", unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&family=JetBrains+Mono:wght@400;500&display=swap');

/* === RESET === */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"], [data-testid="stApp"],
[data-testid="stAppViewContainer"], .main, section.main {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background-color: #F1F5F9 !important;
    color: #0F172A !important;
}
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { visibility: hidden !important; }

/* === HIDE collapse toggle — sidebar is permanently open === */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] { display: none !important; }

.block-container { padding: 0 !important; max-width: 100% !important; }

/* === SIDEBAR — always visible === */
[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
    min-width: 270px !important;
    max-width: 320px !important;
    transform: none !important;
    visibility: visible !important;
    display: block !important;
}
[data-testid="stSidebar"][aria-expanded="false"] {
    transform: none !important;
    margin-left: 0 !important;
    min-width: 270px !important;
    display: block !important;
    visibility: visible !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
}

/* Sidebar dark header */
.sb-header {
    background: linear-gradient(160deg, #0F172A 0%, #1E3A8A 100%);
    padding: 1.4rem 1.2rem 1.3rem 1.2rem;
}
.sb-logo-row {
    display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.75rem;
}
.sb-logo-box {
    width: 34px; height: 34px;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.9rem;
}
.sb-title { font-size: 0.92rem; font-weight: 800; color: #FFFFFF; }
.sb-subtitle { font-size: 0.68rem; color: #93C5FD; margin-top: 0.1rem; }
.sb-stats-row {
    display: flex; gap: 0.45rem; margin-top: 0.9rem;
}
.sb-stat-box {
    flex: 1;
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 8px;
    padding: 0.5rem 0.4rem;
    text-align: center;
}
.sb-stat-val { font-size: 0.95rem; font-weight: 800; color: #FFFFFF; line-height: 1; }
.sb-stat-key { font-size: 0.52rem; font-weight: 700; color: #93C5FD; text-transform: uppercase; letter-spacing: 0.07em; margin-top: 0.12rem; }

/* Sidebar body */
.sb-body { padding: 0.85rem 1rem; }
.sb-card {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 0.85rem 0.9rem;
    margin-bottom: 0.6rem;
}
.sb-card-label {
    font-size: 0.58rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #94A3B8; margin-bottom: 0.4rem;
}
.sb-hint { font-size: 0.69rem; color: #94A3B8; margin-bottom: 0.4rem; }
.lang-chip {
    display: flex; align-items: center; gap: 0.5rem;
    background: #FFFFFF; border: 1.5px solid #E2E8F0;
    border-radius: 8px; padding: 0.42rem 0.7rem; margin-top: 0.4rem;
}
.lc-flag { font-size: 1rem; line-height: 1; }
.lc-name { font-size: 0.8rem; font-weight: 700; color: #0F172A; }
.lc-script { font-size: 0.63rem; color: #94A3B8; margin-top: 0.05rem; }

/* Language list rows */
.ll { display: flex; align-items: center; justify-content: space-between; padding: 0.27rem 0; border-bottom: 1px solid #F1F5F9; }
.ll:last-child { border-bottom: none; }
.ll-l { display: flex; align-items: center; gap: 0.38rem; }
.ll-name { font-size: 0.73rem; font-weight: 600; color: #334155; }
.ll-badge { font-size: 0.58rem; color: #94A3B8; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 999px; padding: 0.04rem 0.4rem; }

/* === TOPBAR === */
.topbar {
    background: #FFFFFF;
    border-bottom: 1px solid #E2E8F0;
    padding: 0 2rem;
    height: 56px;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.tb-brand { display: flex; align-items: center; gap: 0.6rem; }
.tb-icon {
    width: 30px; height: 30px;
    background: linear-gradient(135deg, #1D4ED8, #6366F1);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.8rem;
    box-shadow: 0 2px 8px rgba(99,102,241,0.35);
}
.tb-name { font-weight: 800; font-size: 0.97rem; color: #0F172A; letter-spacing: -0.015em; }
.tb-dot { color: #CBD5E1; font-size: 0.8rem; margin: 0 0.15rem; }
.tb-sub { font-size: 0.7rem; color: #94A3B8; }
.tb-pills { display: flex; gap: 0.4rem; }
.tb-pill {
    background: #F8FAFC; border: 1px solid #E2E8F0;
    border-radius: 999px; padding: 0.2rem 0.7rem;
    font-size: 0.68rem; font-weight: 600; color: #64748B;
}
.tb-pill-hi { background: #EEF2FF; border-color: #C7D2FE; color: #4338CA; }

/* === CONTENT AREA === */
.content { padding: 1.6rem 2rem; }

/* === HERO (split layout) === */
.hero {
    display: flex;
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 1.6rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    min-height: 240px;
}
.hero-left {
    flex: 1.15;
    background: linear-gradient(145deg, #0C1445 0%, #1E3A8A 55%, #1D4ED8 100%);
    padding: 2.2rem 2.5rem;
    position: relative; overflow: hidden;
}
.hero-left::before {
    content: ''; position: absolute;
    top: -70px; right: -50px;
    width: 260px; height: 260px;
    background: radial-gradient(circle, rgba(99,102,241,.4) 0%, transparent 65%);
    pointer-events: none;
}
.hero-left::after {
    content: ''; position: absolute;
    bottom: -50px; left: 25%;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(59,130,246,.2) 0%, transparent 65%);
    pointer-events: none;
}
.hero-badge {
    display: inline-flex; align-items: center; gap: 0.35rem;
    background: rgba(255,255,255,0.09);
    border: 1px solid rgba(255,255,255,0.16);
    border-radius: 999px;
    padding: 0.22rem 0.75rem;
    font-size: 0.6rem; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: #93C5FD; margin-bottom: 0.9rem;
}
.hero-h1 {
    font-size: 1.85rem; font-weight: 800; color: #FFFFFF;
    letter-spacing: -0.03em; line-height: 1.1; margin: 0 0 0.5rem;
}
.hero-h1 em {
    font-style: normal;
    background: linear-gradient(90deg, #60A5FA, #A78BFA);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-desc { font-size: 0.83rem; color: #93C5FD; margin: 0 0 1.6rem; line-height: 1.65; max-width: 380px; }
.hero-kpis { display: flex; gap: 0; align-items: flex-start; }
.hkpi { padding-right: 1.4rem; border-right: 1px solid rgba(255,255,255,0.15); margin-right: 1.4rem; }
.hkpi:last-child { border: none; margin: 0; padding: 0; }
.hkpi-val { font-size: 1.35rem; font-weight: 800; color: #FFFFFF; line-height: 1; }
.hkpi-lbl { font-size: 0.6rem; color: #93C5FD; font-weight: 500; margin-top: 0.15rem; }

.hero-right {
    flex: 0.72;
    background: #F8FAFC;
    border-left: 1px solid #E2E8F0;
    padding: 1.8rem 1.5rem;
    display: flex; flex-direction: column; justify-content: center;
}
.hr-title {
    font-size: 0.58rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #94A3B8; margin-bottom: 0.8rem;
}
.hw-step { display: flex; align-items: flex-start; gap: 0.65rem; padding: 0.48rem 0; border-bottom: 1px solid #E9EEF5; }
.hw-step:last-child { border: none; }
.hw-num {
    width: 21px; height: 21px; min-width: 21px;
    background: linear-gradient(135deg, #1D4ED8, #6366F1);
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.6rem; font-weight: 800; color: #FFFFFF;
    margin-top: 0.05rem;
}
.hw-t { font-size: 0.76rem; font-weight: 700; color: #0F172A; }
.hw-s { font-size: 0.67rem; color: #94A3B8; margin-top: 0.06rem; }

/* === UPLOAD SECTION === */
.up-row {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 0.65rem;
}
.up-label { font-size: 0.6rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #64748B; }
.up-formats { display: flex; gap: 0.3rem; }
.fmt-badge { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 6px; padding: 0.13rem 0.48rem; font-size: 0.64rem; font-weight: 700; color: #475569; }

/* Style ONLY the native Streamlit uploader — no fake one */
[data-testid="stFileUploader"] {
    background: #FFFFFF !important;
    border: 2px dashed #C7D2FE !important;
    border-radius: 14px !important;
    transition: border-color 0.2s, background 0.2s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #6366F1 !important;
    background: #F5F3FF !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
    padding: 1.8rem 1rem !important;
}
/* Browse files button inside uploader */
[data-testid="stFileUploaderDropzone"] button {
    background: linear-gradient(135deg, #1D4ED8, #6366F1) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 9px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.84rem !important;
    padding: 0.5rem 1.4rem !important;
    box-shadow: 0 3px 10px rgba(99,102,241,0.3) !important;
}
[data-testid="stFileUploaderDropzone"] button:hover {
    background: linear-gradient(135deg, #1E40AF, #4F46E5) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 5px 14px rgba(99,102,241,0.4) !important;
}
/* Uploader text */
[data-testid="stFileUploaderDropzoneInstructions"] span {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    color: #0F172A !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] small {
    font-size: 0.77rem !important;
    color: #94A3B8 !important;
}

/* === STATUS BOXES === */
.sbox { border-radius: 10px; padding: 0.75rem 1rem; font-size: 0.81rem; margin: 0.7rem 0; display: flex; align-items: center; gap: 0.5rem; font-weight: 500; }
.sbox-blue  { background: #EFF6FF; border: 1px solid #BFDBFE; color: #1E40AF; border-left: 3px solid #2563EB; }
.sbox-green { background: #F0FDF4; border: 1px solid #BBF7D0; color: #14532D; border-left: 3px solid #16A34A; }
.sbox-amber { background: #FFFBEB; border: 1px solid #FDE68A; color: #78350F; border-left: 3px solid #D97706; }

/* === IMAGE PANEL === */
.img-panel { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 1.1rem; }
.panel-label { font-size: 0.58rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #94A3B8; margin-bottom: 0.65rem; display: flex; align-items: center; gap: 0.3rem; }

/* === INFO PANEL === */
.info-panel { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 1.25rem; }
.ip-title { font-size: 0.9rem; font-weight: 800; color: #0F172A; }
.ip-sub { font-size: 0.69rem; color: #94A3B8; margin: 0.1rem 0 0.9rem; }
.ip-row { display: flex; align-items: center; gap: 0.6rem; padding: 0.4rem 0; border-bottom: 1px solid #F1F5F9; }
.ip-row:last-child { border: none; }
.ip-icon { width: 24px; height: 24px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 0.72rem; flex-shrink: 0; }
.ip-key { font-size: 0.77rem; color: #64748B; width: 115px; flex-shrink: 0; }
.ip-val { font-size: 0.77rem; font-weight: 700; color: #0F172A; }

/* === TAGS === */
.tag { display: inline-flex; align-items: center; padding: 0.17rem 0.55rem; border-radius: 999px; font-size: 0.65rem; font-weight: 700; }
.tag-b { background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }
.tag-s { background: #F8FAFC; color: #475569; border: 1px solid #E2E8F0; }
.tag-p { background: #F5F3FF; color: #6D28D9; border: 1px solid #DDD6FE; }

/* === PAGE COUNTER === */
.pctr { display: inline-flex; align-items: center; gap: 1rem; background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 12px; padding: 0.7rem 1.1rem; margin: 0.6rem 0 1rem; }
.pctr-num { font-size: 1.6rem; font-weight: 800; color: #1D4ED8; line-height: 1; }
.pctr-lbl { font-size: 0.62rem; color: #60A5FA; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; }
.pctr-hint { font-size: 0.77rem; color: #334155; font-weight: 500; }
.pctr-hint small { display: block; font-size: 0.68rem; color: #94A3B8; font-weight: 400; margin-top: 0.1rem; }

/* === PROGRESS === */
.prog-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.05rem 1.25rem; margin: 0.65rem 0; }
.prog-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.15rem; }
.prog-title { font-size: 0.84rem; font-weight: 700; color: #0F172A; }
.prog-right { display: flex; align-items: center; gap: 0.4rem; flex-shrink: 0; margin-left: 0.5rem; }
.prog-pct { font-size: 0.78rem; font-weight: 800; color: #6366F1; }
.prog-sub { font-size: 0.69rem; color: #94A3B8; margin-bottom: 0.6rem; }
.prog-bar-bg { background: #F1F5F9; border-radius: 999px; height: 6px; overflow: hidden; }
.prog-bar { background: linear-gradient(90deg, #1D4ED8, #6366F1); height: 100%; border-radius: 999px; transition: width 0.5s cubic-bezier(.4,0,.2,1); }
.step-pill { display: inline-flex; align-items: center; background: #EEF2FF; border: 1px solid #C7D2FE; border-radius: 999px; padding: 0.14rem 0.52rem; font-size: 0.6rem; font-weight: 700; color: #4338CA; white-space: nowrap; }
.step-pill-done { background: #F0FDF4; border-color: #BBF7D0; color: #15803D; }

/* === RESULT PANEL === */
.result-panel { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 13px; overflow: hidden; margin-bottom: 0.35rem; }
.rp-head { background: #F8FAFC; border-bottom: 1px solid #E2E8F0; padding: 0.72rem 1.1rem; display: flex; align-items: center; gap: 0.55rem; }
.rp-icon { width: 27px; height: 27px; border-radius: 7px; display: flex; align-items: center; justify-content: center; font-size: 0.78rem; }
.rp-icon-b { background: #EFF6FF; }
.rp-icon-p { background: #F5F3FF; }
.rp-title { font-size: 0.82rem; font-weight: 700; color: #0F172A; }
.rp-meta { font-size: 0.66rem; color: #94A3B8; }

/* === KPI ROW === */
.kpi-row { display: flex; gap: 0.6rem; margin: 1.3rem 0; flex-wrap: wrap; }
.kpi-card { flex: 1; min-width: 85px; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 11px; padding: 0.85rem 0.9rem; text-align: center; }
.kpi-val { font-size: 1.5rem; font-weight: 800; color: #1D4ED8; line-height: 1; }
.kpi-label { font-size: 0.58rem; font-weight: 700; color: #94A3B8; margin-top: 0.25rem; letter-spacing: 0.08em; text-transform: uppercase; }

/* === BUTTONS === */
.stButton > button {
    background: linear-gradient(135deg, #1D4ED8 0%, #6366F1 100%) !important;
    color: #FFF !important; border: none !important; border-radius: 10px !important;
    padding: 0.58rem 1.6rem !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.86rem !important; font-weight: 700 !important;
    box-shadow: 0 3px 12px rgba(99,102,241,0.3) !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 5px 18px rgba(99,102,241,0.42) !important; }

.stDownloadButton > button {
    background: #FFFFFF !important; color: #4338CA !important;
    border: 1.5px solid #C7D2FE !important; border-radius: 10px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important; font-weight: 700 !important;
}
.stDownloadButton > button:hover { background: #EEF2FF !important; }

/* === FORM INPUTS === */
.stSelectbox > div > div {
    border-radius: 9px !important; border: 1.5px solid #E2E8F0 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.84rem !important; background: #FFFFFF !important; color: #0F172A !important;
}
.stTextArea textarea {
    border-radius: 9px !important; border: 1.5px solid #E2E8F0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important; line-height: 1.75 !important;
    color: #334155 !important; background: #FAFAFA !important;
}
.stNumberInput input {
    border-radius: 9px !important; border: 1.5px solid #E2E8F0 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background: #FFFFFF !important; color: #0F172A !important;
}
.stCheckbox label { font-size: 0.81rem !important; color: #475569 !important; font-weight: 600 !important; }

/* Divider */
hr { border-color: #E2E8F0 !important; margin: 1.2rem 0 !important; }

/* === FOOTER === */
.footer {
    border-top: 1px solid #E2E8F0; margin-top: 2rem;
    padding: 1.1rem 2rem;
    display: flex; align-items: center; justify-content: space-between;
    background: #FFFFFF; flex-wrap: wrap; gap: 0.6rem;
}
.footer-brand { display: flex; align-items: center; gap: 0.45rem; }
.footer-icon { width: 22px; height: 22px; background: linear-gradient(135deg,#1D4ED8,#6366F1); border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; }
.footer-name { font-size: 0.83rem; font-weight: 800; color: #0F172A; }
.footer-sep { font-size: 0.75rem; color: #CBD5E1; }
.footer-tagline { font-size: 0.72rem; color: #94A3B8; }
.footer-stack { font-size: 0.67rem; color: #CBD5E1; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────
# DATA
# ──────────────────────────────────────────────────────
LANGS = {
    "Hindi":     {"flag": "HI", "script": "Devanagari"},
    "Punjabi":   {"flag": "PA",  "script": "Gurmukhi"},
    "Tamil":     {"flag": "TA", "script": "Tamil"},
    "Telugu":    {"flag": "TE", "script": "Telugu"},
    "Bengali":   {"flag": "BN", "script": "Bengali"},
    "Kannada":   {"flag": "KN", "script": "Kannada"},
    "Malayalam": {"flag": "ML", "script": "Malayalam"},
    "Marathi":   {"flag": "MR", "script": "Devanagari"},
    "Gujarati":  {"flag": "GU", "script": "Gujarati"},
    "English":   {"flag": "EN", "script": "Latin"},
}
TGT_LANGS = ["English","Hindi","Punjabi","Tamil","Telugu","French","Spanish","German"]
TGT_FLAGS = {"English":"EN","Hindi":"HI","Punjabi":"PA","Tamil":"TA",
             "Telugu":"TE","French":"🇫🇷","Spanish":"🇪🇸","German":"🇩🇪"}

# ──────────────────────────────────────────────────────
# SIDEBAR — render ALL html first, then widgets in order
# ──────────────────────────────────────────────────────
with st.sidebar:
    # Dark header (no widgets inside)
    st.markdown("""
    <div class="sb-header">
        <div class="sb-logo-row">
            <div class="sb-logo-box">🔍</div>
            <div>
                <div class="sb-title">BhashaScan</div>
                <div class="sb-subtitle">OCR & Translator</div>
            </div>
        </div>
        <div class="sb-stats-row">
            <div class="sb-stat-box">
                <div class="sb-stat-val">9</div>
                <div class="sb-stat-key">Languages</div>
            </div>
            <div class="sb-stat-box">
                <div class="sb-stat-val">3</div>
                <div class="sb-stat-key">Formats</div>
            </div>
            <div class="sb-stat-box">
                <div class="sb-stat-val">~90%</div>
                <div class="sb-stat-key">Accuracy</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Body wrapper start
    st.markdown('<div class="sb-body">', unsafe_allow_html=True)

    # ── Source language ──
    st.markdown("""
    <div class="sb-card">
        <div class="sb-card-label">📖 Source Language</div>
        <div class="sb-hint">Language in your document</div>
    </div>
    """, unsafe_allow_html=True)
    ocr_lang = st.selectbox("Source language", list(LANGS.keys()),
                            label_visibility="collapsed", key="k_src")
    li = LANGS[ocr_lang]
    st.markdown(f"""
    <div class="lang-chip" style="margin-bottom:0.6rem;">
        <span class="lc-flag">{li['flag']}</span>
        <div>
            <div class="lc-name">{ocr_lang}</div>
            <div class="lc-script">{li['script']} script · Tesseract code: {
                {'Hindi':'hin','Punjabi':'pan','Tamil':'tam','Telugu':'tel',
                 'Bengali':'ben','Kannada':'kan','Malayalam':'mal',
                 'Marathi':'mar','Gujarati':'guj','English':'eng'}.get(ocr_lang,'')
            }</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Target language ──
    st.markdown("""
    <div class="sb-card">
        <div class="sb-card-label">🌐 Translate To</div>
    </div>
    """, unsafe_allow_html=True)
    tgt_lang = st.selectbox("Target language", TGT_LANGS,
                            label_visibility="collapsed", key="k_tgt")
    st.markdown(f"""
    <div class="lang-chip" style="margin-bottom:0.6rem;">
        <span class="lc-flag">{TGT_FLAGS.get(tgt_lang,'🌐')}</span>
        <div class="lc-name">{tgt_lang}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Options ──
    st.markdown('<div class="sb-card"><div class="sb-card-label">⚙️ Options</div>', unsafe_allow_html=True)
    show_pre = st.checkbox("Show preprocessed image", value=False, key="k_pre")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Language list ──
    st.markdown('<div class="sb-card"><div class="sb-card-label">🗂 All Supported Languages</div>', unsafe_allow_html=True)
    rows = ""
    for lang, d in LANGS.items():
        rows += f"""
        <div class="ll">
            <div class="ll-l">
                <span style="font-size:0.9rem;">{d['flag']}</span>
                <span class="ll-name">{lang}</span>
            </div>
            <span class="ll-badge">{d['script']}</span>
        </div>"""
    st.markdown(rows + '</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # end sb-body

# ──────────────────────────────────────────────────────
# TOPBAR
# ──────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
    <div class="tb-brand">
        <div class="tb-icon">🔍</div>
        <span class="tb-name">BhashaScan</span>
        <span class="tb-dot">·</span>
        <span class="tb-sub">Indian Language OCR & Translator</span>
    </div>
    <div class="tb-pills">
        <span class="tb-pill tb-pill-hi">🇮🇳 9 Languages</span>
        <span class="tb-pill">📄 PDF Support</span>
        <span class="tb-pill">🌐 7 Translations</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────
# MAIN CONTENT
# ──────────────────────────────────────────────────────
st.markdown('<div class="content">', unsafe_allow_html=True)

# HERO
st.markdown(f"""
<div class="hero">
    <div class="hero-left">
        <div class="hero-badge">✦ AI-Powered OCR Platform</div>
        <div class="hero-h1">BhashaScan —<br><em>Indian Language OCR</em></div>
        <div class="hero-desc">Extract, digitize and translate text from images & PDFs across 9 Indian regional scripts using Tesseract LSTM engine.</div>
        <div class="hero-kpis">
            <div class="hkpi"><div class="hkpi-val">9</div><div class="hkpi-lbl">Indian Languages</div></div>
            <div class="hkpi"><div class="hkpi-val">JPG·PNG·PDF</div><div class="hkpi-lbl">File Formats</div></div>
            <div class="hkpi"><div class="hkpi-val">~90%</div><div class="hkpi-lbl">OCR Accuracy</div></div>
        </div>
    </div>
    <div class="hero-right">
        <div class="hr-title">⚡ How it works</div>
        <div class="hw-step"><div class="hw-num">1</div><div><div class="hw-t">Upload Document</div><div class="hw-s">Image (JPG/PNG) or multi-page PDF</div></div></div>
        <div class="hw-step"><div class="hw-num">2</div><div><div class="hw-t">Smart Preprocessing</div><div class="hw-s">Auto quality detection + OpenCV filters</div></div></div>
        <div class="hw-step"><div class="hw-num">3</div><div><div class="hw-t">OCR Extraction</div><div class="hw-s">Tesseract LSTM reads {ocr_lang} text</div></div></div>
        <div class="hw-step"><div class="hw-num">4</div><div><div class="hw-t">Translate & Export</div><div class="hw-s">Google Translate → {tgt_lang} + TXT</div></div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# UPLOAD — single native Streamlit uploader only
st.markdown("""
<div class="up-row">
    <span class="up-label">📂 Upload Document</span>
    <div class="up-formats">
        <span class="fmt-badge">JPG</span>
        <span class="fmt-badge">PNG</span>
        <span class="fmt-badge">PDF</span>
        <span class="fmt-badge">Max 200MB</span>
    </div>
</div>
""", unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Drag & drop or click Browse Files — supports JPG, PNG, PDF (max 200MB)",
    type=["jpg", "jpeg", "png", "pdf"],
    key="uploader"
)

# ──────────────────────────────────────────────────────
# PROCESSING
# ──────────────────────────────────────────────────────
if uploaded is not None:
    file_ext = uploaded.name.rsplit(".", 1)[-1].lower()
    is_pdf   = file_ext == "pdf"

    # ── PDF PATH ──────────────────────────────────────
    if is_pdf:
        sz = round(len(uploaded.getvalue()) / 1024 / 1024, 1)
        st.markdown(f"""
        <div class="sbox sbox-blue">
            📄 <strong>{uploaded.name}</strong>
            &emsp;<span class="tag tag-b">PDF</span>
            &emsp;<span class="tag tag-s">{sz} MB</span>
        </div>""", unsafe_allow_html=True)

        pdf_bytes = uploaded.read()
        with st.spinner("Reading PDF structure..."):
            total_pages = get_pdf_page_count(pdf_bytes)

        st.markdown(f"""
        <div class="pctr">
            <div>
                <div class="pctr-num">{total_pages}</div>
                <div class="pctr-lbl">Pages Detected</div>
            </div>
            <div class="pctr-hint">
                Select the page range to process.
                <small>Tip: start with 1–3 pages to test first.</small>
            </div>
        </div>""", unsafe_allow_html=True)

        ca, cb = st.columns(2)
        with ca: s_pg = st.number_input("From page", min_value=1, max_value=total_pages, value=1, key="s_pg")
        with cb: e_pg = st.number_input("To page",   min_value=1, max_value=total_pages, value=min(3, total_pages), key="e_pg")

        n_sel = int(e_pg) - int(s_pg) + 1
        if n_sel > 10:
            st.markdown(f'<div class="sbox sbox-amber">⚠️ <strong>{n_sel} pages selected.</strong> This may take several minutes — consider processing smaller batches.</div>', unsafe_allow_html=True)

        if st.button(f"🔍  Extract & Translate  {n_sel} Page{'s' if n_sel>1 else ''}", key="pdf_btn"):
            prog_slot = st.empty()

            def show_prog(label, sub, pct, step, done=False):
                pill_cls = "step-pill-done" if done else "step-pill"
                pill_txt = f"✓ Step {step}/3" if done else f"Step {step}/3"
                prog_slot.markdown(f"""
                <div class="prog-card">
                    <div class="prog-top">
                        <div>
                            <div class="prog-title">{label}</div>
                            <div class="prog-sub">{sub}</div>
                        </div>
                        <div class="prog-right">
                            <span class="{pill_cls}">{pill_txt}</span>
                            <span class="prog-pct">{pct}%</span>
                        </div>
                    </div>
                    <div class="prog-bar-bg">
                        <div class="prog-bar" style="width:{pct}%"></div>
                    </div>
                </div>""", unsafe_allow_html=True)

            show_prog("⚙️ Converting PDF pages to images", "Rendering at 300 DPI for max OCR accuracy", 10, 1)
            pages = pdf_to_images(pdf_bytes=pdf_bytes, start_page=int(s_pg), end_page=int(e_pg))

            if not pages:
                st.markdown('<div class="sbox sbox-amber">❌ Could not convert PDF. File may be corrupted or password-protected.</div>', unsafe_allow_html=True)
            else:
                ext_all, trs_all = [], []
                bar = st.progress(0)

                for i, pg in enumerate(pages):
                    pct = int((i + 1) / len(pages) * 100)
                    show_prog(
                        f"🔤 Processing page {int(s_pg)+i} of {int(e_pg)}",
                        f"OCR extraction + {tgt_lang} translation",
                        10 + int(pct * 0.88), 2
                    )
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as t:
                        pg.save(t.name, "JPEG"); tp = t.name
                    cleaned    = preprocess(tp)
                    extracted  = extract_text(cleaned, ocr_lang)
                    translated = translate_text(extracted, tgt_lang)
                    ext_all.append(f"━━ Page {int(s_pg)+i} ━━\n{extracted}")
                    trs_all.append(f"━━ Page {int(s_pg)+i} ━━\n{translated}")
                    os.unlink(tp)
                    bar.progress((i + 1) / len(pages))

                show_prog("✅ Processing complete", "All pages extracted and translated", 100, 3, done=True)
                st.markdown('<div class="sbox sbox-green">✅ <strong>All pages processed!</strong> Results are displayed below.</div>', unsafe_allow_html=True)

                full_e = "\n\n".join(ext_all)
                full_t = "\n\n".join(trs_all)

                st.divider()
                rc1, rc2 = st.columns(2, gap="large")
                with rc1:
                    st.markdown(f'<div class="result-panel"><div class="rp-head"><div class="rp-icon rp-icon-b">🔤</div><div><div class="rp-title">Extracted Text</div><div class="rp-meta">{li["flag"]} {ocr_lang} · {li["script"]}</div></div></div></div>', unsafe_allow_html=True)
                    st.text_area("extracted", full_e, height=380, key="pdf_ext", label_visibility="collapsed")
                with rc2:
                    st.markdown(f'<div class="result-panel"><div class="rp-head"><div class="rp-icon rp-icon-p">🌐</div><div><div class="rp-title">Translation</div><div class="rp-meta">{TGT_FLAGS.get(tgt_lang,"🌐")} {tgt_lang}</div></div></div></div>', unsafe_allow_html=True)
                    st.text_area("translated", full_t, height=380, key="pdf_trs", label_visibility="collapsed")

                st.markdown(f"""
                <div class="kpi-row">
                    <div class="kpi-card"><div class="kpi-val">{len(pages)}</div><div class="kpi-label">Pages</div></div>
                    <div class="kpi-card"><div class="kpi-val">{len(full_e.split())}</div><div class="kpi-label">Words</div></div>
                    <div class="kpi-card"><div class="kpi-val">{len(full_e)}</div><div class="kpi-label">Characters</div></div>
                    <div class="kpi-card"><div class="kpi-val">{len(full_e.splitlines())}</div><div class="kpi-label">Lines</div></div>
                </div>""", unsafe_allow_html=True)

                out = f"EXTRACTED ({ocr_lang}):\n{full_e}\n\nTRANSLATED ({tgt_lang}):\n{full_t}"
                st.download_button("📥  Download Results as TXT", data=out,
                    file_name="bhashascan_results.txt", mime="text/plain", key="pdf_dl")

    # ── IMAGE PATH ────────────────────────────────────
    else:
        image = Image.open(uploaded)
        ic1, ic2 = st.columns([1, 1], gap="large")

        with ic1:
            st.markdown('<div class="img-panel"><div class="panel-label">📷 Original Image</div>', unsafe_allow_html=True)
            st.image(image, use_container_width=True)
            st.markdown(f"""
            <div style="display:flex;gap:0.35rem;flex-wrap:wrap;margin-top:0.55rem;">
                <span class="tag tag-s">📐 {image.width}×{image.height}px</span>
                <span class="tag tag-s">{file_ext.upper()}</span>
                <span class="tag tag-b">{li['flag']} {ocr_lang}</span>
            </div></div>""", unsafe_allow_html=True)

        with ic2:
            st.markdown(f"""
            <div class="info-panel">
                <div class="ip-title">Ready to Process</div>
                <div class="ip-sub">Configure settings in the sidebar, then click below</div>
                <div class="ip-row">
                    <div class="ip-icon" style="background:#EEF2FF;">📖</div>
                    <div class="ip-key">Source language</div>
                    <div class="ip-val">{li['flag']} {ocr_lang} ({li['script']})</div>
                </div>
                <div class="ip-row">
                    <div class="ip-icon" style="background:#F5F3FF;">🌐</div>
                    <div class="ip-key">Translate to</div>
                    <div class="ip-val">{TGT_FLAGS.get(tgt_lang,'🌐')} {tgt_lang}</div>
                </div>
                <div class="ip-row">
                    <div class="ip-icon" style="background:#F0FDF4;">🔧</div>
                    <div class="ip-key">Preprocessing</div>
                    <div class="ip-val">Auto (Smart Detection)</div>
                </div>
                <div class="ip-row">
                    <div class="ip-icon" style="background:#FFF7ED;">🧠</div>
                    <div class="ip-key">OCR engine</div>
                    <div class="ip-val">Tesseract LSTM (OEM 3)</div>
                </div>
                <div class="ip-row">
                    <div class="ip-icon" style="background:#FDF4FF;">📐</div>
                    <div class="ip-key">Resolution</div>
                    <div class="ip-val">{image.width} × {image.height} px</div>
                </div>
            </div>""", unsafe_allow_html=True)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as t:
            t.write(uploaded.getvalue()); tp = t.name

        st.markdown("<div style='height:0.7rem'></div>", unsafe_allow_html=True)

        if st.button("🔍  Extract & Translate", key="img_btn"):
            slot = st.empty()
            res  = {}

            STEPS = [
                ("🔧", "Preprocessing image",   "Applying smart quality detection + OpenCV filters"),
                ("🔤", "Running OCR extraction", f"Tesseract LSTM reading {ocr_lang} text"),
                ("🌐", "Translating text",       f"Google Translate → {tgt_lang}"),
            ]

            for i, (icon, title, sub) in enumerate(STEPS):
                pct = int((i + 1) / 3 * 100)
                slot.markdown(f"""
                <div class="prog-card">
                    <div class="prog-top">
                        <div>
                            <div class="prog-title">{icon} {title}</div>
                            <div class="prog-sub">{sub}</div>
                        </div>
                        <div class="prog-right">
                            <span class="step-pill">Step {i+1}/3</span>
                            <span class="prog-pct">{pct}%</span>
                        </div>
                    </div>
                    <div class="prog-bar-bg">
                        <div class="prog-bar" style="width:{pct}%"></div>
                    </div>
                </div>""", unsafe_allow_html=True)

                if i == 0:
                    res["cleaned"] = preprocess(tp)
                    if show_pre:
                        with ic1:
                            st.markdown('<div class="panel-label" style="margin-top:0.9rem;">🔧 Preprocessed</div>', unsafe_allow_html=True)
                            st.image(res["cleaned"], use_container_width=True)
                elif i == 1:
                    res["extracted"]  = extract_text(res["cleaned"], ocr_lang)
                elif i == 2:
                    res["translated"] = translate_text(res["extracted"], tgt_lang)
                time.sleep(0.25)

            slot.markdown('<div class="sbox sbox-green">✅ <strong>Complete!</strong> Extraction and translation finished successfully.</div>', unsafe_allow_html=True)

            st.divider()
            rc1, rc2 = st.columns(2, gap="large")
            et = res["extracted"]
            tt = res["translated"]

            with rc1:
                st.markdown(f'<div class="result-panel"><div class="rp-head"><div class="rp-icon rp-icon-b">🔤</div><div><div class="rp-title">Extracted Text</div><div class="rp-meta">{li["flag"]} {ocr_lang} · {li["script"]}</div></div></div></div>', unsafe_allow_html=True)
                st.text_area("extracted", et, height=300, key="img_ext", label_visibility="collapsed")
            with rc2:
                st.markdown(f'<div class="result-panel"><div class="rp-head"><div class="rp-icon rp-icon-p">🌐</div><div><div class="rp-title">Translation</div><div class="rp-meta">{TGT_FLAGS.get(tgt_lang,"🌐")} {tgt_lang}</div></div></div></div>', unsafe_allow_html=True)
                st.text_area("translated", tt, height=300, key="img_trs", label_visibility="collapsed")

            st.markdown(f"""
            <div class="kpi-row">
                <div class="kpi-card"><div class="kpi-val">{len(et.split())}</div><div class="kpi-label">Words</div></div>
                <div class="kpi-card"><div class="kpi-val">{len(et)}</div><div class="kpi-label">Characters</div></div>
                <div class="kpi-card"><div class="kpi-val">{len(et.splitlines())}</div><div class="kpi-label">Lines</div></div>
                <div class="kpi-card"><div class="kpi-val">{image.width}×{image.height}</div><div class="kpi-label">Resolution</div></div>
            </div>""", unsafe_allow_html=True)

            out = f"EXTRACTED ({ocr_lang}):\n{et}\n\nTRANSLATED ({tgt_lang}):\n{tt}"
            st.download_button("📥  Download Results as TXT", data=out,
                file_name="bhashascan_results.txt", mime="text/plain", key="img_dl")

        os.unlink(tp)

st.markdown('</div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    <div class="footer-brand">
        <div class="footer-icon">🔍</div>
        <span class="footer-name">BhashaScan</span>
        <span class="footer-sep">·</span>
        <span class="footer-tagline">Indian Language OCR & Translator</span>
    </div>
    <div class="footer-stack">Python · Tesseract OCR · OpenCV · Google Translate · Streamlit</div>
</div>
""", unsafe_allow_html=True)