import pytesseract
import platform
from PIL import Image
import io
import os
from openai import OpenAI
import base64

def configure_tesseract_path():
    system = platform.system()
    if system == "Windows":
        # Common default install location—change if needed
        possible = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
        ]
        for path in possible:
            if os.path.isfile(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break
        else:
            raise FileNotFoundError("Tesseract not found in default Windows paths.")
    else:
        # On Linux or macOS, tesseract should be in PATH
        pytesseract.pytesseract.tesseract_cmd = "tesseract"

    # Optional: verify it's working
    try:
        version = os.popen(f'"{pytesseract.pytesseract.tesseract_cmd}" --version').read()
        print("✔️ Tesseract detected:", version.splitlines()[0])
    except Exception as e:
        raise RuntimeError(f"Error verifying Tesseract at '{pytesseract.pytesseract.tesseract_cmd}': {e}")



def extract_text_from_image(image_path_or_bytes):
    configure_tesseract_path()

    if isinstance(image_path_or_bytes, bytes):
        image = Image.open(io.BytesIO(image_path_or_bytes))
    else:
        image = Image.open(image_path_or_bytes)

    # Step 1: OCR text extraction
    ocr_text = pytesseract.image_to_string(image)

    # Step 2: Prepare image for OpenAI
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    b64 = base64.b64encode(buffered.getvalue()).decode()
    data_uri = f"data:image/jpeg;base64,{b64}"

    # Step 3: LLM-based image description
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-4.1-mini",  # Make sure this is a vision-capable model
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What's in this image?"},
                    {"type": "image_url", "image_url": {"url": data_uri}}
                ]
            }
        ],
        max_tokens=300
    )

    image_description = response.choices[0].message.content

    # Step 4: Combine and return
    return f"{ocr_text.strip()}\n\n**Image Description:**\n{image_description.strip()}"