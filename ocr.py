import fitz
import pytesseract
from PIL import Image
import io


def extract_text_from_pdf(pdf_path):
    """
    First tries normal PDF text extraction using PyMuPDF.
    If very little text is found, falls back to OCR using Tesseract.
    """

    doc = fitz.open(pdf_path)

    extracted_text = ""

    # Try normal PDF text extraction
    for page in doc:
        extracted_text += page.get_text()

    # If text was successfully extracted
    if len(extracted_text.strip()) > 100:
        return extracted_text

    # Otherwise perform OCR
    extracted_text = ""

    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

        image_bytes = pix.tobytes("png")
        image = Image.open(io.BytesIO(image_bytes))

        text = pytesseract.image_to_string(image)

        extracted_text += text + "\n"

    return extracted_text