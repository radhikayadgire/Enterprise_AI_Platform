"""Stub email sender - simulates sending until a real SMTP integration exists."""

import re

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def send_email(to: str, subject: str, body: str) -> dict:
    if not to or not _EMAIL_RE.match(to):
        raise ValueError(f"invalid recipient email address: {to!r}")
    if not subject or not subject.strip():
        raise ValueError("subject must not be empty")
    if not body or not body.strip():
        raise ValueError("body must not be empty")

    return {"to": to, "subject": subject, "status": "sent"}
