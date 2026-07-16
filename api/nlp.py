import spacy
import re

nlp = spacy.load("en_core_web_sm")


# -----------------------------------
# CLEAN OCR TEXT (IMPROVED)
# -----------------------------------
def clean_text(text):

    # remove UI-like words (IMPORTANT FIX)
    noise_words = [
        "upload", "document", "drag", "drop", "analyze",
        "extract", "structured", "data", "results",
        "analysis", "completed", "successfully"
    ]

    text = text.lower()

    for word in noise_words:
        text = text.replace(word, " ")

    # keep only useful characters
    text = re.sub(r"[^\w\s@.+:/-]", " ", text)

    # remove multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# -----------------------------------
# NLP EXTRACTION
# -----------------------------------
def extract_data(text):

    try:

        cleaned_text = clean_text(text)

        doc = nlp(cleaned_text)

        structured_data = {
            "organizations": [],
            "dates": [],
            "emails": [],
            "phone_numbers": [],
            "amounts": []
        }

        # ---------------------------
        # ENTITIES (ORG + DATE)
        # ---------------------------
        for ent in doc.ents:

            if ent.label_ == "ORG":
                org = ent.text.strip()

                if len(org) > 2:
                    structured_data["organizations"].append(org)

            elif ent.label_ == "DATE":
                date = ent.text.strip()

                if len(date) > 3:
                    structured_data["dates"].append(date)

        # ---------------------------
        # EMAILS
        # ---------------------------
        structured_data["emails"] = re.findall(
            r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
            cleaned_text
        )

        # ---------------------------
        # PHONE NUMBERS (IMPROVED)
        # ---------------------------
        structured_data["phone_numbers"] = re.findall(
            r"\+?\d[\d\s-]{8,15}\d",
            cleaned_text
        )

        # ---------------------------
        # AMOUNTS (SMART FILTER)
        # ---------------------------
        raw_amounts = re.findall(r"\$?\d+(?:\.\d{1,2})?", cleaned_text)

        filtered = []

        for a in raw_amounts:
            try:
                val = float(a.replace("$", ""))

                # remove junk numbers like 1,2,3,10 etc
                if 50 <= val <= 1000000:
                    filtered.append(a)

            except:
                pass

        structured_data["amounts"] = filtered

        # ---------------------------
        # REMOVE DUPLICATES + EMPTY STRINGS
        # ---------------------------
        for key in structured_data:
            structured_data[key] = list(
                set(
                    [x for x in structured_data[key] if x and len(x) > 2]
                )
            )

        return structured_data

    except Exception as e:

        return {
            "error": f"NLP Error: {str(e)}"
        }