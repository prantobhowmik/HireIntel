from pypdf import PdfReader
import io
import base64

def extract_text_from_pdf(base64_string: str) -> str:
    """
    Extracts text from a base64 encoded PDF string.
    """
    if "," in base64_string:
        base64_string = base64_string.split(",")[1]
    
    pdf_bytes = base64.b64decode(base64_string)
    reader = PdfReader(io.BytesIO(pdf_bytes))
    
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    return text.strip()
