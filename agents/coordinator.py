"""Routes free-form chat messages to the appropriate specialist agent."""

from agents.hr_agent import handle as hr_handle

_HR_KEYWORDS = ("leave", "insurance", "policy", "benefit", "hr")


def route(message: str) -> dict:
    if not message or not message.strip():
        raise ValueError("message must not be empty")

    message_lower = message.lower()
    if any(keyword in message_lower for keyword in _HR_KEYWORDS):
        return {"agent": "hr_agent", "response": hr_handle(message)}
    return {"agent": "search_agent", "response": "I couldn't find a specialist for that request."}
