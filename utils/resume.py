from typing import Optional
from pypdf import PdfReader

def extract_text_from_pdf(uploaded_file) -> str:
    """
    uploaded_file: streamlit UploadedFile
    returns plain text
    """
    reader = PdfReader(uploaded_file)
    chunks = []
    for page in reader.pages:
        txt = page.extract_text() or ""
        chunks.append(txt)
    return "\n".join(chunks)

def limit_text(t: str, max_chars: int = 8000) -> str:
    t = t.strip()
    if len(t) <= max_chars:
        return t
    return t[:max_chars] + "\n\n[truncated]"
