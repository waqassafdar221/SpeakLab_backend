import logging
import smtplib
from email.message import EmailMessage
from .db import settings
from .email_templates import invite_email_text, invite_email_html

logger = logging.getLogger(__name__)


def send_invite_email(to_email: str, username: str, token: str) -> bool:
    """Send the "set your password" invite link. Returns False (and logs)
    on any failure instead of raising — a bounced email shouldn't fail
    account creation."""
    if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("SMTP not configured; skipping invite email to %s", to_email)
        return False

    link = f"{settings.FRONTEND_BASE_URL.rstrip('/')}/set-password?token={token}"

    msg = EmailMessage()
    msg["Subject"] = "You've been invited to SpeakStudio"
    msg["From"] = settings.SMTP_FROM or settings.SMTP_USER
    msg["To"] = to_email
    msg.set_content(invite_email_text(username, link))
    msg.add_alternative(invite_email_html(username, link), subtype="html")

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
            smtp.starttls()
            smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception:
        logger.exception("Failed to send invite email to %s", to_email)
        return False
