# %%
import os
import fitz  # PyMuPDF
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st
import pytesseract
from PIL import Image
import io
import tempfile
from docx import Document

# %%
load_dotenv()  # Load environment variables from .env file

# %%
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Make sure to set this securely

# %%
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# %%
def extract_text_from_image(image_path_or_bytes):
    if isinstance(image_path_or_bytes, bytes):
        image = Image.open(io.BytesIO(image_path_or_bytes))
    else:
        image = Image.open(image_path_or_bytes)
    return pytesseract.image_to_string(image)

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""

    for page_num, page in enumerate(doc):
        text += f"\n--- Page {page_num + 1} ---\n"
        # Extract text
        page_text = page.get_text()
        if page_text:
            text += page_text

        # Extract images for OCR
        images = page.get_images(full=True)
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            ocr_text = extract_text_from_image(image_bytes)
            text += f"\n[Image {img_index + 1} OCR]:\n{ocr_text}\n"

    doc.close()
    return text.strip()

def extract_text_from_docx(file_path):
    text = ""
    doc = Document(file_path)

    # Extract plain text
    for para in doc.paragraphs:
        text += para.text + "\n"

    # Extract images and apply OCR
    for rel in doc.part._rels:
        rel_obj = doc.part._rels[rel]
        if "image" in rel_obj.target_ref:
            image_data = rel_obj.target_part.blob
            ocr_text = extract_text_from_image(image_data)
            text += f"\n[Image OCR from DOCX]:\n{ocr_text}\n"
    return text.strip()

def extract_text_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    elif ext == '.txt':
        return extract_text_from_txt(file_path)
    elif ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
        return extract_text_from_image(file_path)
    else:
        return f"Unsupported file format: {ext}"


# %%
file_path = "../files/Initial Implementation Plan - AI-Driven Document Compliance Analysis System (3).pdf"  # Replace with your file path
result_text = extract_text(file_path)
print("📄 Extracted Text:\n")
print(result_text)

# %%
def analyze_with_iso_27001_2022(text):
    system_prompt = """
You are a certified ISO/IEC 27001:2022 lead auditor and cybersecurity expert.

Your task is to assess whether the following document content aligns with the ISO/IEC 27001:2022 standard for Information Security Management Systems (ISMS).

### Perform the following:
1. Identify key points in the text related to information security, governance, risk management, roles, policies, technical controls, physical security, business continuity, cloud usage, etc.
2. Compare these areas against the ISO 27001:2022 requirements:
   - **Clause 4-10**: Organizational context, leadership, planning, support, operation, performance evaluation, and continual improvement.
   - **Annex A Controls (Themes)**:
     - A.5: Organizational Controls
     - A.6: People Controls
     - A.7: Physical Controls
     - A.8: Technological Controls
3. Identify if the document demonstrates full, partial, or no compliance for each relevant clause or control.
4. Provide a summarized **compliance report** that includes:
   - Compliant areas ✅
   - Non-compliant or partially compliant areas ❌
   - Key evidence or gaps found in the text
   - Suggested improvements where applicable
   - An overall **compliance score (0–100%)**

### Important:
- Be thorough, cite clauses where applicable (e.g., A.5.23 or Clause 6.1.2).
- If the document is only partially compliant or unclear in some areas, mention that and suggest what is missing.
- Keep your response structured.

Now, analyze the following document content for compliance:
\"\"\"{}\"\"\"
""".format(text)

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content


# %%
def review_and_suggest_fixes(report):
    prompt = f"""
You are an ISO/IEC 27001:2022 implementation expert.

The following report outlines non-compliant or partially compliant areas from a compliance assessment.

Your job is to:
- Review the issues found.
- Suggest specific, actionable improvements for each area.
- Provide examples, templates, or documentation suggestions if needed.
- Clearly indicate which ISO 27001:2022 clause or control each suggestion relates to.

Here is the report:
\"\"\"{report}\"\"\"
"""
    
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": prompt}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content


# %%
# file_path = "example_security_policy.pdf"
# extracted_text = extract_text(file_path)

print("🔍 Running ISO 27001:2022 compliance audit...\n")
iso_report = analyze_with_iso_27001_2022(result_text)
print(iso_report)

# if "❌" in iso_report or "partially compliant" in iso_report.lower():
print("\n🔁 Running improvement suggestions based on non-compliance...\n")
revision_notes = review_and_suggest_fixes(iso_report)
print(revision_notes)

# %%



