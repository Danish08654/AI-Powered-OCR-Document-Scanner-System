import streamlit as st
import requests
from PIL import Image

# PAGE CONFIG
st.set_page_config(
    page_title="OCR Document Scanner",
    page_icon="📄",
    layout="wide"
)

# CUSTOM STYLING
st.markdown("""
    <style>
        .main {
            background-color: #0e1117;
        }

        h1 {
            text-align: center;
            color: #4CAF50;
        }

        .stFileUploader {
            border: 2px dashed #4CAF50;
            padding: 20px;
            border-radius: 10px;
        }

        .box {
            background-color: #1c1f26;
            padding: 20px;
            border-radius: 12px;
            margin-top: 20px;
        }

        .title {
            color: #4CAF50;
            font-size: 18px;
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# HEADER
st.title("📄 OCR Document Scanner")

# UPLOAD SECTION
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📤 Upload Document")
    file = st.file_uploader(
        "Choose an image (PNG, JPG, JPEG)",
        type=["png", "jpg", "jpeg"]
    )

    if file:
        st.image(file, caption="Uploaded Image", use_container_width=True)

# PROCESS BUTTON
if file and st.button("⚡ Extract Data"):

    with st.spinner("Processing document..."):

        try:
            response = requests.post(
                "http://localhost:8000/analyze",
                files={"file": file},
                timeout=60
            )

            if response.status_code != 200:
                st.error(f"Server Error: {response.status_code}")
                st.json(response.text)
                st.stop()

            data = response.json()

        except requests.exceptions.RequestException as e:
            st.error("Failed to connect to backend API")
            st.exception(e)
            st.stop()

    # -----------------------------
    # SAFE EXTRACTION (FIXED)
    # -----------------------------
    extracted_text = data.get("text", "No text returned")

    # ✅ FIXED KEY HERE
    structured_data = data.get("structured_data", {})

    st.success("Analysis Complete!")

    col1, col2 = st.columns(2)

    # RAW TEXT
    with col1:
        st.markdown('<div class="box">', unsafe_allow_html=True)
        st.markdown('<div class="title">🧾 Extracted Text</div>', unsafe_allow_html=True)
        st.write(extracted_text)
        st.markdown('</div>', unsafe_allow_html=True)

    # STRUCTURED DATA
    with col2:
        st.markdown('<div class="box">', unsafe_allow_html=True)
        st.markdown('<div class="title">📊 Structured Data</div>', unsafe_allow_html=True)

        # 🔥 Better check (not just empty dict)
        if structured_data and any(structured_data.values()):
            st.json(structured_data)
        else:
            st.warning("No meaningful structured data found")
            st.json(structured_data)

        st.markdown('</div>', unsafe_allow_html=True)