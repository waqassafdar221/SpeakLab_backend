import secrets
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session
from .models import User
from .auth import hash_pw

INVITE_VALID_HOURS = 48


def create_user_row(
    db: Session,
    *,
    username: str,
    email: str,
    role: str,
    vendor_id: int | None = None,
    package_id: int | None = None,
    initial_credits: int = 0,
    monthly_price: float = 0,
) -> User:
    """Create a user row for any role, pending activation via an emailed invite
    link — no password is set here. Customers get a 30-day expiry; admin and
    vendor accounts don't expire."""
    if db.query(User).filter((User.username == username) | (User.email == email)).first():
        raise HTTPException(400, "Username or email exists")

    u = User(
        username=username,
        email=email,
        password_hash=hash_pw(secrets.token_urlsafe(32)),  # unusable placeholder until invite is accepted
        role=role,
        vendor_id=vendor_id,
        credits=initial_credits,
        package_id=package_id,
        monthly_price=monthly_price,
        expiry_date=datetime.now() + timedelta(days=30) if role == "customer" else None,
        invite_token=secrets.token_urlsafe(32),
        invite_expires_at=datetime.now() + timedelta(hours=INVITE_VALID_HOURS),
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u
