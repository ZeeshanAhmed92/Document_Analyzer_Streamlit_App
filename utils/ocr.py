import pytesseract
import platform
from PIL import Image
import io
import os

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
    return pytesseract.image_to_string(image)
