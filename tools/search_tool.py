"""Simple keyword search across local reference documents.

Kept dependency-free (no external search API) so the agent works offline.
"""
from pathlib import Path

from pypdf import PdfReader

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _iter_documents():
    if not DATA_DIR.exists():
        return
    for path in DATA_DIR.glob("*.pdf"):
        yield path


def search(query: str) -> list[dict]:
    query_lower = query.lower()
    results = []
    for path in _iter_documents():
        if path.stat().st_size == 0:
            continue
        try:
            reader = PdfReader(str(path))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception:
            continue
        if query_lower in text.lower():
            results.append({"document": path.name, "snippet": text[:200]})
    return results
