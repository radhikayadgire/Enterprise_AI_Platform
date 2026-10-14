"""Answers HR questions (leave policy, insurance) using local reference docs."""
from tools.hr_tool import search_hr_documents


class HRAgent:
    name = "hr_agent"

    def handle(self, query: str) -> str:
        return search_hr_documents(query)
