"""Mock email tool used by the EmailAgent."""


def send_email(to: str, subject: str, body: str) -> dict:
    if not to or "@" not in to:
        raise ValueError(f"invalid recipient address: {to!r}")
    if not subject or not subject.strip():
        raise ValueError("subject must not be empty")
    return {"to": to, "subject": subject, "status": "sent"}
