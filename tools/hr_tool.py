"""Lookup helpers over the HR reference documents in data/."""
from pathlib import Path

from pypdf import PdfReader

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

DOCUMENTS = {
    "leave": DATA_DIR / "leave.pdf",
    "insurance": DATA_DIR / "insurance.pdf",
}


def _extract_text(pdf_path: Path) -> str:
    if not pdf_path.exists() or pdf_path.stat().st_size == 0:
        return ""
    try:
        reader = PdfReader(str(pdf_path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:
        # Corrupt/placeholder PDFs shouldn't crash the agent.
        return ""


def search_hr_documents(query: str) -> str:
    """Search leave/insurance policy documents for a keyword match."""
    query_lower = query.lower()
    topic = "insurance" if "insurance" in query_lower else "leave"
    text = _extract_text(DOCUMENTS[topic])

    if not text:
        return (
            f"The '{topic}' policy document is currently unavailable or empty. "
            "Please contact HR directly for up-to-date information."
        )

    matches = [line for line in text.splitlines() if query_lower in line.lower()]
    if matches:
        return "\n".join(matches[:5])
    return f"No direct match found in the {topic} policy document for: '{query}'."
