"""Coordinator agent that routes a user query to the right specialist agent."""

from agents.email_agent import EmailAgent
from agents.hr_agent import HRAgent
from agents.search_agent import SearchAgent


class Coordinator:
    def __init__(self):
        self.hr_agent = HRAgent()
        self.email_agent = EmailAgent()
        self.search_agent = SearchAgent()

    def route(self, query: str) -> str:
        if not query or not query.strip():
            raise ValueError("query must not be empty")
        lowered = query.lower()
        if any(word in lowered for word in ("leave", "insurance", "policy", "hr")):
            return self.hr_agent.run(query)
        if "email" in lowered or "send" in lowered:
            raise ValueError("email requests require to/subject/body; use the /api/email endpoint")
        return self.search_agent.run(query)
