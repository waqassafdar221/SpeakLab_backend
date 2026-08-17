import logging
import smtplib
from email.message import EmailMessage
from .db import settings
from .email_templates import (
    invite_email_text, invite_email_html,
    reset_password_email_text, reset_password_email_html,
    low_credit_email_text, low_credit_email_html,
    expiry_soon_email_text, expiry_soon_email_html,
)

logger = logging.getLogger(__name__)


def _send(to_email: str, subject: str, text_body: str, html_body: str) -> bool:
    """Shared SMTP send. Returns False (and logs) on any failure instead of
    raising — a bounced email shouldn't fail the request that triggered it."""
    if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("SMTP not configured; skipping email to %s", to_email)
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM or settings.SMTP_USER
    msg["To"] = to_email
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
            smtp.starttls()
            smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception:
        logger.exception("Failed to send email to %s", to_email)
        return False


def send_invite_email(to_email: str, username: str, token: str) -> bool:
    link = f"{settings.FRONTEND_BASE_URL.rstrip('/')}/set-password?token={token}"
    return _send(
        to_email,
        "You've been invited to SpeakStudio",
        invite_email_text(username, link),
        invite_email_html(username, link),
    )


def send_reset_password_email(to_email: str, username: str, token: str) -> bool:
    link = f"{settings.FRONTEND_BASE_URL.rstrip('/')}/reset-password?token={token}"
    return _send(
        to_email,
        "Reset your SpeakStudio password",
        reset_password_email_text(username, link),
        reset_password_email_html(username, link),
    )


def send_low_credit_email(to_email: str, username: str, credits: int) -> bool:
    link = f"{settings.FRONTEND_BASE_URL.rstrip('/')}/dashboard"
    return _send(
        to_email,
        "You're running low on credits",
        low_credit_email_text(username, credits, link),
        low_credit_email_html(username, credits, link),
    )


def send_expiry_soon_email(to_email: str, username: str, expiry_label: str) -> bool:
    link = f"{settings.FRONTEND_BASE_URL.rstrip('/')}/dashboard"
    return _send(
        to_email,
        "Your SpeakStudio account expires soon",
        expiry_soon_email_text(username, expiry_label, link),
        expiry_soon_email_html(username, expiry_label, link),
    )
