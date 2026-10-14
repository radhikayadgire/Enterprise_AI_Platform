"""Email sending helper used by the email agent.

Falls back to a dry-run (no network call) when SMTP credentials are not
configured, which keeps local/dev/test runs working without real mail
infrastructure.
"""
import smtplib
from email.message import EmailMessage

from backend.config import settings


def send_email(to_address: str, subject: str, body: str) -> dict:
    if not settings.SMTP_HOST:
        return {
            "status": "dry-run",
            "to": to_address,
            "subject": subject,
            "body": body,
            "detail": "SMTP_HOST not configured; email was not actually sent.",
        }

    message = EmailMessage()
    message["From"] = settings.SMTP_FROM_ADDRESS
    message["To"] = to_address
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        if settings.SMTP_USERNAME:
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(message)

    return {"status": "sent", "to": to_address, "subject": subject}
