import fitz  # PyMuPDF
import docx
import os

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file.
    """
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text.strip()

def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text from a DOCX file.
    """
    doc = docx.Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs]).strip()

def extract_text(file_path: str) -> str:
    """
    Determine file type and extract text accordingly.
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
