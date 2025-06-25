import pymupdf
from utils.ocr import extract_text_from_image

def extract_text_from_pdf(file_path):
    doc = pymupdf.open(file_path)
    text = ""
    for page_num, page in enumerate(doc):
        text += f"\n--- Page {page_num + 1} ---\n"
        text += page.get_text()
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            ocr_text = extract_text_from_image(image_bytes)
            text += f"\n[Image {img_index + 1} OCR]:\n{ocr_text}\n"
    return text
