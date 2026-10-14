"""Routes an incoming chat message to the most relevant specialised agent."""
from agents.email_agent import EmailAgent
from agents.hr_agent import HRAgent
from agents.search_agent import SearchAgent

_EMAIL_KEYWORDS = ("email", "send a mail", "mail to")
_HR_KEYWORDS = ("leave", "insurance", "hr policy", "benefits")


class Coordinator:
    def __init__(self) -> None:
        self.hr_agent = HRAgent()
        self.email_agent = EmailAgent()
        self.search_agent = SearchAgent()

    def route(self, query: str) -> dict:
        query_lower = query.lower()

        if any(keyword in query_lower for keyword in _EMAIL_KEYWORDS):
            agent = self.email_agent
        elif any(keyword in query_lower for keyword in _HR_KEYWORDS):
            agent = self.hr_agent
        else:
            agent = self.search_agent

        return {"agent": agent.name, "response": agent.handle(query)}


coordinator = Coordinator()
