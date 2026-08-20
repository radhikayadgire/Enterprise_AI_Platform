from tools.email_tool import send_email


def handle(to: str, subject: str, body: str) -> dict:
    return send_email(to, subject, body)
