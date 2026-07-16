from fastapi import FastAPI, UploadFile, File
import shutil
import os

from preprocess import preprocess_image
from ocr import extract_text
from nlp import extract_data
from utils import allowed_file, create_upload_folder

app = FastAPI()

UPLOAD_FOLDER = create_upload_folder()


@app.get("/")
def home():
    return {
        "message": "OCR Document Scanner API Running"
    }


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):

    file_path = None

    try:

        # -----------------------------
        # Validate File Type
        # -----------------------------
        if not allowed_file(file.filename):
            return {
                "success": False,
                "error": "Only PNG, JPG, JPEG files allowed"
            }

        # -----------------------------
        # Save File
        # -----------------------------
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # -----------------------------
        # Preprocess Image
        # -----------------------------
        processed_image = preprocess_image(file_path)

        # -----------------------------
        # OCR Extraction
        # -----------------------------
        extracted_text = extract_text(processed_image)

        # -----------------------------
        # OCR FAILURE HANDLING
        # -----------------------------
        if not extracted_text or "OCR Error" in str(extracted_text):
            return {
                "success": False,
                "filename": file.filename,
                "text": extracted_text,
                "structured_data": {},
                "error": "OCR failed (Tesseract not installed or image unreadable)"
            }

        # -----------------------------
        # NLP Structured Extraction
        # -----------------------------
        structured_data = extract_data(extracted_text)

        # -----------------------------
        # FINAL SUCCESS RESPONSE
        # -----------------------------
        return {
            "success": True,
            "filename": file.filename,
            "text": extracted_text,
            "structured_data": structured_data
        }

    except Exception as e:

        return {
            "success": False,
            "filename": file.filename if file else None,
            "text": "",
            "structured_data": {},
            "error": str(e)
        }

    finally:
        # Optional cleanup (good practice)
        if file_path and os.path.exists(file_path):
            pass  # keep file for debugging OR delete if you want