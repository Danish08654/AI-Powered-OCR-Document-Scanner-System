import streamlit as st
import numpy as np
from PIL import Image
import io
import re

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ScanIQ · Free OCR Scanner",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── HERO ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div style="display:flex;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:18px;">
    <div class="hero-badge"><span class="dot"></span>Powered by EasyOCR</div>
    <div class="free-badge">✦ 100% Free</div>
  </div>
  <h1 class="hero-title">Extract text from<br><span>any document</span></h1>
  <p class="hero-sub">Upload a photo, receipt, form, or handwritten note — ScanIQ reads it instantly. No API key. No cost. Ever.</p>
</div>
""", unsafe_allow_html=True)

# ── LANGUAGE MAP ─────────────────────────────────────────────────────────────
LANG_MAP = {
    "English":  "en",
    "Urdu":     "ur",
    "Arabic":   "ar",
    "French":   "fr",
    "German":   "de",
    "Spanish":  "es",
    "Chinese (Simplified)": "ch_sim",
    "Hindi":    "hi",
    "Japanese": "ja",
    "Korean":   "ko",
    "Russian":  "ru",
    "Turkish":  "tr",
}

# ── EASYOCR READER (cached) ───────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_reader(lang_codes: tuple):
    return easyocr.Reader(list(lang_codes), gpu=False)

# ── OCR FUNCTION ──────────────────────────────────────────────────────────────
def run_ocr(pil_image: Image.Image, lang_codes: tuple):
    reader = get_reader(lang_codes)
    img_np = np.array(pil_image.convert("RGB"))
    results = reader.readtext(img_np)          # list of (bbox, text, confidence)
    return results

def parse_results(results):
    lines       = [r[1] for r in results]
    confidences = [r[2] for r in results]
    full_text   = "\n".join(lines)
    avg_conf    = sum(confidences) / len(confidences) if confidences else 0
    return full_text, lines, confidences, avg_conf

def extract_structured(text: str) -> dict:
    """Heuristic extraction of common fields."""
    fields = {}
    # Email
    emails = re.findall(r"[\w.\-+]+@[\w.\-]+\.[a-z]{2,}", text, re.I)
    if emails: fields["email"] = emails[0]
    # Phone
    phones = re.findall(r"(?:\+?\d[\d\s\-().]{7,}\d)", text)
    if phones: fields["phone"] = phones[0].strip()
    # Date
    dates = re.findall(r"\b\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}\b", text)
    if dates: fields["date"] = dates[0]
    # Total / Amount
    amounts = re.findall(r"(?:total|amount|Rs\.?|PKR|USD|\$|€|£)\s*[:\-]?\s*[\d,]+(?:\.\d{1,2})?", text, re.I)
    if amounts: fields["amount"] = amounts[0].strip()
    # Invoice / Order number
    inv = re.findall(r"(?:invoice|order|bill|ref)[#\s\-:no.]*(\w+)", text, re.I)
    if inv: fields["invoice_number"] = inv[0]
    # Website / URL
    urls = re.findall(r"https?://\S+|www\.\S+", text, re.I)
    if urls: fields["website"] = urls[0]
    return fields

def conf_color(c: float) -> str:
    if c >= 0.85: return "#22C55E"
    if c >= 0.60: return "#F59E0B"
    return "#EF4444"

# ── CONTENT ───────────────────────────────────────────────────────────────────
st.markdown('<div class="content-area">', unsafe_allow_html=True)

# Language picker + upload row
lang_col, upload_col = st.columns([0.9, 1.1])

with lang_col:
    st.markdown('<span class="section-label">🌐 Languages in document</span>', unsafe_allow_html=True)
    chosen_langs = st.multiselect(
        "langs",
        options=list(LANG_MAP.keys()),
        default=["English"],
        label_visibility="collapsed",
    )
    if not chosen_langs:
        st.warning("Pick at least one language.")
        st.stop()

    lang_codes = tuple(LANG_MAP[l] for l in chosen_langs)

    st.markdown("""
    <div class="tip-box" style="margin-top:18px;">
      <div class="tip-title">💡 Works great on</div>
      <ul class="tip-list">
        <li>Receipts &amp; invoices</li>
        <li>Handwritten notes</li>
        <li>Business cards</li>
        <li>Forms &amp; ID cards</li>
        <li>Whiteboards &amp; signage</li>
        <li>Screenshots of text</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)

with upload_col:
    st.markdown('<span class="section-label">📂 Upload document</span>', unsafe_allow_html=True)
    file = st.file_uploader(
        "drop-zone",
        type=["png", "jpg", "jpeg", "webp", "bmp"],
        label_visibility="collapsed",
    )

    if file:
        st.markdown('<div class="preview-wrap">', unsafe_allow_html=True)
        st.image(file, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.button("⚡  Scan & Extract Text", key="scan_btn", use_container_width=True)
    else:
        st.markdown("""
        <div class="empty-state">
          <div class="icon">🗂️</div>
          <p>Drop a <strong>PNG</strong>, <strong>JPG</strong>, <strong>WEBP</strong>, or <strong>BMP</strong><br>here to get started</p>
        </div>
        """, unsafe_allow_html=True)

# ── SCAN ─────────────────────────────────────────────────────────────────────
if file and st.session_state.get("scan_btn"):

    st.markdown("""
    <div class="scan-divider">
      <div class="scan-divider-line"></div>
      <div class="scan-divider-label">Scan Results</div>
      <div class="scan-divider-line"></div>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("🔍  Reading document… (first run downloads language models)"):
        try:
            pil_img   = Image.open(file)
            results   = run_ocr(pil_img, lang_codes)
        except Exception as e:
            st.error(f"OCR failed: {e}")
            st.stop()

    if not results:
        st.warning("No text detected. Try a clearer image or add more languages.")
        st.stop()

    full_text, lines, confidences, avg_conf = parse_results(results)
    structured  = extract_structured(full_text)
    word_count  = len(full_text.split())
    char_count  = len(full_text)

    # Success banner
    st.markdown(f"""
    <div class="success-banner">
      <span class="chk">✓</span>
      Found <strong>{len(lines)} text regions</strong> with
      <strong>{avg_conf*100:.0f}% average confidence</strong> — results below.
    </div>
    """, unsafe_allow_html=True)

    # ── STATS ──
    st.markdown("""
    <div class="result-card stats-card" style="margin-bottom:22px;">
      <div class="card-title"><span class="card-icon">📈</span>Scan Summary</div>
    """, unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    stats = [
        (len(lines),              "Regions"),
        (word_count,              "Words"),
        (char_count,              "Characters"),
        (f"{avg_conf*100:.0f}%",  "Avg Confidence"),
    ]
    for col, (val, lbl) in zip([s1, s2, s3, s4], stats):
        with col:
            st.markdown(f"""
            <div class="stat-pill">
              <div class="val">{val}</div>
              <div class="lbl">{lbl}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── TEXT + STRUCTURED + CONFIDENCE ──
    c1, c2, c3 = st.columns([1.2, 0.9, 0.9])

    with c1:
        st.markdown("""
        <div class="result-card text-card">
          <div class="card-title"><span class="card-icon">📝</span>Extracted Text</div>
        """, unsafe_allow_html=True)
        st.markdown(
            f'<div class="text-box">{full_text}</div>',
            unsafe_allow_html=True,
        )
        # Copy-friendly textarea hidden behind expander
        with st.expander("📋 Copy raw text"):
            st.text_area("", full_text, height=160, label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="result-card data-card">
          <div class="card-title"><span class="card-icon">📊</span>Structured Fields</div>
        """, unsafe_allow_html=True)
        if structured:
            st.json(structured)
        else:
            st.markdown("""
            <div style="text-align:center;padding:38px 16px;color:#4B5563;
                        font-size:13px;font-family:'Inter',sans-serif;">
              <div style="font-size:28px;margin-bottom:8px;">🔎</div>
              No common fields detected.<br>
              <span style="font-size:11px;color:#374151;">
                Works best on receipts,<br>invoices &amp; business cards.
              </span>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="result-card conf-card">
          <div class="card-title"><span class="card-icon">🎯</span>Confidence</div>
        """, unsafe_allow_html=True)
        # Show top 12 lines by confidence (desc)
        paired = sorted(zip(lines, confidences), key=lambda x: -x[1])[:12]
        rows_html = ""
        for txt, conf in paired:
            pct   = int(conf * 100)
            color = conf_color(conf)
            short = (txt[:28] + "…") if len(txt) > 29 else txt
            rows_html += f"""
            <div class="conf-row">
              <div class="conf-text" title="{txt}">{short}</div>
              <div class="conf-bar-wrap">
                <div class="conf-bar" style="width:{pct}%;background:{color};"></div>
              </div>
              <div class="conf-pct">{pct}%</div>
            </div>"""
        st.markdown(rows_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
