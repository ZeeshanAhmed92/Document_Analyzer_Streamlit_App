import pymupdf
from docx import Document
from utils.ocr import extract_text_from_image
from PIL import Image
import io
import base64
import fitz  # PyMuPDF
import os


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

def extract_pdf_as_markdown(file_path):
    doc = fitz.open(file_path)
    markdown = ""

    for page_num, page in enumerate(doc):
        markdown += f"\n## Page {page_num + 1}\n"
        markdown += page.get_text("text") + "\n"

        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            ext = base_image["ext"]
            image_filename = f"page{page_num+1}_img{img_index+1}.{ext}"

            # OCR image text
            ocr_text = extract_text_from_image(image_bytes)
            markdown += f"\n**Image {img_index + 1} OCR:**\n```\n{ocr_text.strip()}\n```\n"
            markdown += f"![Image {img_index + 1}]({image_filename})\n"

    return markdown

def extract_docx_as_markdown(file_path):
    doc = Document(file_path)
    markdown = ""
    image_count = 0

    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            markdown += text + "\n\n"

    # Extract and process images (if needed)
    rels = doc.part._rels
    for rel in rels:
        rel_obj = rels[rel]
        if "image" in rel_obj.target_ref:
            image_count += 1
            image_data = rel_obj.target_part.blob
            ext = rel_obj.target_ref.split(".")[-1]
            image_filename = f"image{image_count}.{ext}"

            # OCR the image
            ocr_text = extract_text_from_image(image_data)
            markdown += f"\n**Image {image_count} OCR:**\n```\n{ocr_text.strip()}\n```\n"
            markdown += f"![Image {image_count}]({image_filename})\n"

    return markdown