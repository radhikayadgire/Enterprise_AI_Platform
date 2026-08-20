"""Agent that composes and sends emails using the email tool."""

from tools.email_tool import send_email


class EmailAgent:
    def run(self, to: str, subject: str, body: str) -> dict:
        return send_email(to, subject, body)
