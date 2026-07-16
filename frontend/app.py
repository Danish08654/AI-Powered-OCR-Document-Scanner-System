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

/*  UPLOAD  */
.section-label {
    font-family:'Space Grotesk',sans-serif;
    font-size:12px; font-weight:700;
    letter-spacing:.1em; text-transform:uppercase;
    color:#6366F1; margin-bottom:10px; display:block;
}
[data-testid="stFileUploader"] {
    background:rgba(99,102,241,.04) !important;
    border:1.5px dashed rgba(99,102,241,.32) !important;
    border-radius:14px !important;
    transition:border-color .2s, background .2s;
}
[data-testid="stFileUploader"]:hover {
    border-color:rgba(99,102,241,.65) !important;
    background:rgba(99,102,241,.08) !important;
}
[data-testid="stFileUploader"] section { padding:28px 20px !important; }

/* ── PREVIEW ── */
.preview-wrap {
    margin-top:18px; border-radius:14px;
    overflow:hidden; border:1px solid rgba(99,102,241,.18);
}
[data-testid="stImage"] img { border-radius:14px !important; }

/* ── BUTTON ── */
[data-testid="stButton"] > button {
    width:100%;
    background:linear-gradient(135deg,#4F46E5,#6366F1) !important;
    color:#fff !important; border:none !important;
    border-radius:12px !important; padding:14px 28px !important;
    font-family:'Space Grotesk',sans-serif !important;
    font-size:15px !important; font-weight:600 !important;
    letter-spacing:.02em !important;
    transition:all .2s ease !important;
    box-shadow:0 4px 24px rgba(99,102,241,.32) !important;
    margin-top:14px !important;
}
[data-testid="stButton"] > button:hover {
    transform:translateY(-2px) !important;
    box-shadow:0 8px 32px rgba(99,102,241,.52) !important;
    background:linear-gradient(135deg,#4338CA,#4F46E5) !important;
}
[data-testid="stButton"] > button:active { transform:translateY(0) !important; }

/* ── DIVIDER ── */
.scan-divider {
    display:flex; align-items:center; gap:14px;
    margin:38px 0 28px;
}
.scan-divider-line {
    flex:1; height:1px;
    background:linear-gradient(90deg,transparent,rgba(99,102,241,.28),transparent);
}
.scan-divider-label {
    font-family:'Space Grotesk',sans-serif;
    font-size:11px; font-weight:600;
    letter-spacing:.14em; text-transform:uppercase; color:#374151;
}

/* ── RESULT CARDS ── */
.result-card {
    background:rgba(15,20,40,.6);
    border:1px solid rgba(99,102,241,.14);
    border-radius:18px; padding:26px 26px 22px;
    position:relative; overflow:hidden;
}
.result-card::before {
    content:''; position:absolute;
    top:0;left:0;right:0; height:2px;
    border-radius:18px 18px 0 0;
}
.text-card::before   { background:linear-gradient(90deg,#6366F1,#818CF8); }
.data-card::before   { background:linear-gradient(90deg,#22D3EE,#67E8F9); }
.stats-card::before  { background:linear-gradient(90deg,#F59E0B,#FCD34D); }
.conf-card::before   { background:linear-gradient(90deg,#EC4899,#F472B6); }

.card-title {
    font-family:'Space Grotesk',sans-serif;
    font-size:11.5px; font-weight:700;
    letter-spacing:.12em; text-transform:uppercase;
    margin-bottom:16px;
    display:flex; align-items:center; gap:8px;
}
.text-card  .card-title { color:#818CF8; }
.data-card  .card-title { color:#22D3EE; }
.stats-card .card-title { color:#FCD34D; }
.conf-card  .card-title { color:#F472B6; }

.card-icon {
    width:26px; height:26px; border-radius:7px;
    display:inline-flex; align-items:center;
    justify-content:center; font-size:13px;
}
.text-card  .card-icon { background:rgba(99,102,241,.14); }
.data-card  .card-icon { background:rgba(34,211,238,.12); }
.stats-card .card-icon { background:rgba(245,158,11,.12); }
.conf-card  .card-icon { background:rgba(236,72,153,.12); }

/* ── TEXT OUTPUT ── */
.text-box {
    background:rgba(8,12,20,.65);
    border:1px solid rgba(99,102,241,.11);
    border-radius:11px; padding:16px 18px;
    font-family:'JetBrains Mono',monospace;
    font-size:12.5px; line-height:1.75;
    color:#C4C9E2; max-height:380px;
    overflow-y:auto; white-space:pre-wrap; word-break:break-word;
}
.text-box::-webkit-scrollbar { width:4px; }
.text-box::-webkit-scrollbar-track { background:transparent; }
.text-box::-webkit-scrollbar-thumb {
    background:rgba(99,102,241,.28); border-radius:4px;
}

/* ── CONFIDENCE TABLE ── */
.conf-row {
    display:flex; align-items:center;
    gap:12px; padding:7px 0;
    border-bottom:1px solid rgba(99,102,241,.07);
    font-family:'JetBrains Mono',monospace;
    font-size:12px;
}
.conf-row:last-child { border-bottom:none; }
.conf-text { flex:1; color:#C4C9E2; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.conf-bar-wrap { width:80px; height:6px; background:rgba(255,255,255,.07); border-radius:99px; flex-shrink:0; }
.conf-bar { height:6px; border-radius:99px; }
.conf-pct { width:38px; text-align:right; color:#6B7280; font-size:11px; flex-shrink:0; }

/* ── STAT PILLS ── */
.stat-row { display:flex; flex-wrap:wrap; gap:10px; margin-top:4px; }
.stat-pill {
    background:rgba(245,158,11,.08);
    border:1px solid rgba(245,158,11,.2);
    border-radius:8px; padding:10px 16px;
    font-family:'Space Grotesk',sans-serif;
    flex:1; min-width:90px;
}
.stat-pill .val { font-size:22px; font-weight:700; color:#FCD34D; line-height:1; margin-bottom:4px; }
.stat-pill .lbl { font-size:11px; font-weight:500; color:#6B7280; letter-spacing:.07em; text-transform:uppercase; }

/* ── SUCCESS BANNER ── */
.success-banner {
    background:linear-gradient(135deg,rgba(16,185,129,.08),rgba(34,211,238,.06));
    border:1px solid rgba(16,185,129,.24);
    border-radius:12px; padding:13px 18px;
    margin-bottom:22px;
    display:flex; align-items:center; gap:11px;
    font-family:'Space Grotesk',sans-serif;
    font-size:14px; font-weight:500; color:#34D399;
}
.success-banner .chk {
    width:22px; height:22px;
    background:rgba(16,185,129,.14);
    border-radius:50%;
    display:flex; align-items:center; justify-content:center;
    font-size:12px; flex-shrink:0;
}

/* ── EMPTY + TIPS ── */
.empty-state {
    margin-top:18px;
    background:rgba(99,102,241,.03);
    border:1px solid rgba(99,102,241,.09);
    border-radius:14px; padding:32px 24px; text-align:center;
}
.empty-state .icon { font-size:40px; margin-bottom:10px; }
.empty-state p {
    font-family:'Space Grotesk',sans-serif;
    font-size:13.5px; color:#374151; line-height:1.65; margin:0;
}
.empty-state strong { color:#818CF8; }

.tip-box {
    background:rgba(99,102,241,.05);
    border:1px solid rgba(99,102,241,.13);
    border-radius:12px; padding:18px 20px; margin-top:0;
}
.tip-title {
    font-family:'Space Grotesk',sans-serif;
    font-size:11px; font-weight:700;
    letter-spacing:.1em; text-transform:uppercase;
    color:#4B5563; margin-bottom:12px;
}
.tip-list { list-style:none; margin:0; padding:0; }
.tip-list li {
    font-size:13px; color:#4B5563;
    line-height:1.65; padding:3px 0 3px 18px;
    position:relative;
}
.tip-list li::before { content:'›'; position:absolute; left:0; color:#6366F1; font-weight:700; }

/* ── COLS ── */
[data-testid="stHorizontalBlock"] { gap:22px !important; align-items:stretch !important; }
[data-testid="stColumn"] { padding:0 !important; }
</style>
""", unsafe_allow_html=True)

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
