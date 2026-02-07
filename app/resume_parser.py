import pdfplumber
import docx
import re

def clean_text(text: str) -> str:
    # Remove special characters, multiple spaces, and newlines breaking sentences
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text) # Remove non-ASCII
    return text.strip()

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return clean_text(text)

def extract_text_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    text = " ".join([para.text for para in doc.paragraphs])
    return clean_text(text)