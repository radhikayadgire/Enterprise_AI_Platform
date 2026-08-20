"""Mock HR knowledge-base tool backed by documents in data/."""

from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
KNOWN_TOPICS = ("leave", "insurance")


def lookup_policy(question: str) -> str:
    if not question or not question.strip():
        raise ValueError("question must not be empty")
    lowered = question.lower()
    topic = next((t for t in KNOWN_TOPICS if t in lowered), None)
    if topic is None:
        return "No matching HR policy document found for your question."
    return f"Based on {topic}.pdf: please refer to the {topic} policy document for details."
