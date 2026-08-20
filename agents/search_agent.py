"""Agent that answers queries using the search tool."""

from tools.search_tool import search


class SearchAgent:
    def run(self, query: str) -> str:
        return search(query)
