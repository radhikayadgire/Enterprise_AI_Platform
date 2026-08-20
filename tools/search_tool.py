"""Simple in-memory document index over the HR policy PDFs."""

_DOCUMENTS = [
    {"id": "leave-policy", "title": "Leave Policy", "keywords": ["leave", "pto", "vacation"]},
    {"id": "insurance-policy", "title": "Insurance Policy", "keywords": ["insurance", "medical", "health"]},
]


def search_documents(query: str):
    if not query or not query.strip():
        raise ValueError("query must not be empty")

    query_lower = query.lower()
    return [
        {"id": doc["id"], "title": doc["title"]}
        for doc in _DOCUMENTS
        if any(keyword in query_lower for keyword in doc["keywords"])
    ]
