"""Mock search tool used by the SearchAgent."""


def search(query: str) -> str:
    if not query or not query.strip():
        raise ValueError("query must not be empty")
    return f"Top result for '{query}': No live search backend configured; returning a placeholder result."
