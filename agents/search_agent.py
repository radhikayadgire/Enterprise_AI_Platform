"""Searches local reference documents for a keyword."""
from tools.search_tool import search


class SearchAgent:
    name = "search_agent"

    def handle(self, query: str) -> str:
        results = search(query)
        if not results:
            return f"No documents matched '{query}'."
        lines = [f"- {r['document']}: {r['snippet']}" for r in results]
        return "\n".join(lines)
