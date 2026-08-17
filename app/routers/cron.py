from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from ..db import get_db, settings
from ..models import User
from ..email_service import send_low_credit_email, send_expiry_soon_email

router = APIRouter(prefix="/internal/cron", tags=["cron"])


def _check_cron_secret(authorization: str | None = Header(default=None)):
    if not settings.CRON_SECRET or authorization != f"Bearer {settings.CRON_SECRET}":
        raise HTTPException(401, "Unauthorized")


@router.get("/notifications")
def send_notifications(db: Session = Depends(get_db), _=Depends(_check_cron_secret)):
    """Daily check (Vercel Cron, see vercel.json) for customers running low on
    credits or nearing expiry. Each condition emails once — tracked via the
    *_notified_at columns — not on every run."""
    now = datetime.now()

    low_credit_customers = db.query(User).filter(
        User.role == "customer",
        User.credits <= settings.LOW_CREDIT_THRESHOLD,
        User.low_credit_notified_at.is_(None),
    ).all()
    low_credit_sent = 0
    for u in low_credit_customers:
        if send_low_credit_email(u.email, u.username, u.credits):
            u.low_credit_notified_at = now
            low_credit_sent += 1
    db.commit()

    expiry_cutoff = now + timedelta(days=settings.EXPIRY_WARNING_DAYS)
    expiring_customers = db.query(User).filter(
        User.role == "customer",
        User.expiry_date.isnot(None),
        User.expiry_date > now,
        User.expiry_date <= expiry_cutoff,
        User.expiry_notified_at.is_(None),
    ).all()
    expiry_sent = 0
    for u in expiring_customers:
        label = u.expiry_date.strftime("%B %-d, %Y")
        if send_expiry_soon_email(u.email, u.username, label):
            u.expiry_notified_at = now
            expiry_sent += 1
    db.commit()

    return {
        "low_credit_checked": len(low_credit_customers),
        "low_credit_sent": low_credit_sent,
        "expiry_checked": len(expiring_customers),
        "expiry_sent": expiry_sent,
    }
