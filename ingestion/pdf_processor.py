from pathlib import Path
import re


def extract_pdf(path):
    path = Path(path)
    if path.suffix.lower() == ".txt": return path.read_text(encoding="utf-8")
    try:
        from pypdf import PdfReader
        return "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)
    except Exception as error:
        raise ValueError(f"Unable to read PDF {path.name}: {error}") from error

def chunk_text(text, document_name, page_number=1, chunk_size=700):
    cleaned = re.sub(r"\s+", " ", text).strip()
    words = cleaned.split()
    chunks = []
    for start in range(0, len(words), chunk_size):
        value = " ".join(words[start:start + chunk_size])
        if value: chunks.append({"document_name": document_name, "page_number": page_number, "section": "regulatory guidance", "chunk_id": f"{document_name}-{start}", "text": value})
    return chunks

def ingest_regulations(directory):
    from rag.vector_store import save_documents
    documents = []
    for path in Path(directory).glob("*"):
        if path.suffix.lower() not in {".pdf", ".txt"}: continue
        try: documents.extend(chunk_text(extract_pdf(path), path.name))
        except ValueError: continue
    save_documents(documents); return documents
