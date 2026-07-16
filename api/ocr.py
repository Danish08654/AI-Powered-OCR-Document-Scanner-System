import pytesseract

# REQUIRED FOR WINDOWS
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text(image):

    try:
        text = pytesseract.image_to_string(
            image,
            config="--oem 3 --psm 4"
        )

        text = text.strip()

        if not text:
            return "OCR Error: No text detected"

        return text

    except Exception as e:
        return f"OCR Error: {str(e)}"