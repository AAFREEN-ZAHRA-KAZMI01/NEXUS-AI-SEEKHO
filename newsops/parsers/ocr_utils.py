import base64
import io

import pytesseract
from pytesseract import Output
from PIL import Image
from pdf2image import convert_from_bytes


def pdf_to_images(file_bytes: bytes, dpi: int = 150, max_pages: int = 10) -> list:
    return convert_from_bytes(file_bytes, dpi=dpi, first_page=1, last_page=max_pages)


def image_to_base64(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=85)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def run_tesseract_ocr(image: Image.Image) -> dict:
    text = pytesseract.image_to_string(image, lang="eng", config="--oem 3 --psm 6")
    data = pytesseract.image_to_data(image, output_type=Output.DICT)

    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if len(stripped) < 3:
            continue
        non_alpha = sum(1 for c in stripped if not c.isalnum() and not c.isspace())
        if non_alpha / max(len(stripped), 1) > 0.7:
            continue
        cleaned_lines.append(stripped)

    cleaned_text = "\n".join(cleaned_lines)
    return {
        "text": cleaned_text,
        "word_data": data,
        "word_count": len(cleaned_text.split()),
    }


def is_scanned_page(text: str) -> bool:
    return len(text.strip()) < 50
