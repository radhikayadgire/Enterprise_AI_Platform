"""Handles natural-language requests to send an email.

Expects queries shaped like: "email <address> about <subject>: <body>".
Falls back to a generic acknowledgement if the pattern doesn't match.
"""
import re

from tools.email_tool import send_email

_PATTERN = re.compile(
    r"email\s+(?:to\s+)?(?P<to>[\w.+-]+@[\w-]+\.[\w.-]+)\s+about\s+(?P<subject>[^:]+):?\s*(?P<body>.*)",
    re.IGNORECASE,
)


class EmailAgent:
    name = "email_agent"

    def handle(self, query: str) -> str:
        match = _PATTERN.search(query)
        if not match:
            return (
                "I couldn't find an email address and subject in that request. "
                "Try: 'email jane@company.com about Leave Request: I'd like to request leave.'"
            )

        result = send_email(
            to_address=match.group("to").strip(),
            subject=match.group("subject").strip(),
            body=match.group("body").strip() or "(no message body provided)",
        )
        if result["status"] == "sent":
            return f"Email sent to {result['to']} with subject '{result['subject']}'."
        return f"Email queued (dry-run) to {result['to']} with subject '{result['subject']}'."
