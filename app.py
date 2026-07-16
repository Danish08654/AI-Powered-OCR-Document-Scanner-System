import streamlit as st
import numpy as np
from PIL import Image
import re
import easyocr
import json
import html

st.set_page_config(
    page_title="AI Document Scanner",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
.block-container{max-width:1300px;padding-top:1.5rem;padding-bottom:2rem;}
.stApp{background:#f4f7fb;}
.hero{
background:linear-gradient(135deg,#2563eb,#7c3aed);
color:white;padding:42px;border-radius:24px;
text-align:center;box-shadow:0 12px 40px rgba(0,0,0,.15);
margin-bottom:25px;}
.hero h1{margin:0;font-size:46px;}
.hero p{font-size:18px;opacity:.95}
.card{background:white;border-radius:18px;padding:20px;
border:1px solid #e5e7eb;box-shadow:0 8px 24px rgba(0,0,0,.06);}
.text-box{background:#f8fafc;border-radius:12px;padding:16px;
white-space:pre-wrap;border:1px solid #e5e7eb;font-family:Consolas,monospace;}
.stButton>button{
width:100%;height:52px;border-radius:14px;border:none;
background:linear-gradient(90deg,#2563eb,#7c3aed);
color:white;font-weight:700;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>📄 AI Document Scanner</h1>
<p>Upload receipts, invoices, forms, IDs or handwritten notes and extract text instantly.</p>
</div>
""", unsafe_allow_html=True)

LANG_MAP = {
    "English":"en","Urdu":"ur","Arabic":"ar","French":"fr","German":"de",
    "Spanish":"es","Chinese (Simplified)":"ch_sim","Hindi":"hi",
    "Japanese":"ja","Korean":"ko","Russian":"ru","Turkish":"tr",
}

@st.cache_resource
def get_reader(codes):
    return easyocr.Reader(list(codes), gpu=False)

def extract_structured(text):
    d={}
    m=re.findall(r"[\w.\-+]+@[\w.\-]+\.[a-z]{2,}",text,re.I)
    if m:d["email"]=m[0]
    return d

left,right=st.columns([1,1.3])

with left:
    langs=st.multiselect("Languages",list(LANG_MAP),default=["English"])
    uploaded=st.file_uploader("Upload",type=["png","jpg","jpeg","bmp","webp"])

with right:
    if uploaded:
        st.image(uploaded,use_container_width=True)

scan=st.button("⚡ Scan & Extract Text")

if uploaded and scan:
    img=Image.open(uploaded).convert("RGB")
    with st.spinner("Scanning..."):
        reader=get_reader(tuple(LANG_MAP[x] for x in langs))
        res=reader.readtext(np.array(img))
    text="\n".join(r[1] for r in res)
    conf=sum(r[2] for r in res)/len(res) if res else 0
    st.success(f"Average confidence: {conf:.0%}")
    c1,c2=st.columns([2,1])
    with c1:
        st.markdown('<div class="card"><h3>Extracted Text</h3></div>',unsafe_allow_html=True)
        st.markdown(f'<div class="text-box">{html.escape(text)}</div>',unsafe_allow_html=True)
        st.download_button("Download TXT",text,"ocr_output.txt")
    with c2:
        data=extract_structured(text)
        st.json(data)
        st.download_button("Download JSON",json.dumps(data,indent=2),"structured.json")
