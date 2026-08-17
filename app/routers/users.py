import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User
from ..schemas import LoginReq, TokenResp, ChangePasswordReq, SetPasswordReq, ForgotPasswordReq, ResetPasswordReq
from ..auth import verify_pw, hash_pw, make_token
from ..deps import current_user
from ..email_service import send_reset_password_email

RESET_VALID_HOURS = 1

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResp)
def login(body: LoginReq, db: Session = Depends(get_db)):
    identifier = (body.username or "").strip()
    u = db.query(User).filter(
        (User.username == identifier) | (User.email == identifier)
    ).first()
    if not u or not verify_pw(body.password, u.password_hash):
        raise HTTPException(401, "Invalid credentials")
    return TokenResp(access_token=make_token(u.username, u.role))


def _find_valid_invite(db: Session, token: str) -> User:
    u = db.query(User).filter(User.invite_token == token).first()
    if not u:
        raise HTTPException(404, "Invite link not found")
    if not u.invite_expires_at or u.invite_expires_at < datetime.now(u.invite_expires_at.tzinfo):
        raise HTTPException(410, "Invite link has expired")
    return u


@router.get("/invite/{token}")
def get_invite(token: str, db: Session = Depends(get_db)):
    u = _find_valid_invite(db, token)
    return {"username": u.username, "email": u.email}


@router.post("/set-password", response_model=TokenResp)
def set_password(body: SetPasswordReq, db: Session = Depends(get_db)):
    u = _find_valid_invite(db, body.token)
    if len(body.password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters")
    u.password_hash = hash_pw(body.password)
    u.invite_token = None
    u.invite_expires_at = None
    db.commit()
    return TokenResp(access_token=make_token(u.username, u.role))


@router.post("/forgot-password")
def forgot_password(body: ForgotPasswordReq, db: Session = Depends(get_db)):
    GENERIC_MSG = {"message": "If an account exists for that email, we've sent a reset link."}
    u = db.query(User).filter(User.email == body.email).first()
    if not u:
        return GENERIC_MSG  # don't reveal whether the email is registered
    u.reset_token = secrets.token_urlsafe(32)
    u.reset_expires_at = datetime.now() + timedelta(hours=RESET_VALID_HOURS)
    db.commit()
    send_reset_password_email(u.email, u.username, u.reset_token)
    return GENERIC_MSG


def _find_valid_reset(db: Session, token: str) -> User:
    u = db.query(User).filter(User.reset_token == token).first()
    if not u:
        raise HTTPException(404, "Reset link not found")
    if not u.reset_expires_at or u.reset_expires_at < datetime.now(u.reset_expires_at.tzinfo):
        raise HTTPException(410, "Reset link has expired")
    return u


@router.get("/reset/{token}")
def get_reset(token: str, db: Session = Depends(get_db)):
    u = _find_valid_reset(db, token)
    return {"username": u.username, "email": u.email}


@router.post("/reset-password", response_model=TokenResp)
def reset_password(body: ResetPasswordReq, db: Session = Depends(get_db)):
    u = _find_valid_reset(db, body.token)
    if len(body.password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters")
    u.password_hash = hash_pw(body.password)
    u.reset_token = None
    u.reset_expires_at = None
    db.commit()
    return TokenResp(access_token=make_token(u.username, u.role))

users_router = APIRouter(prefix="/users", tags=["users"])

@users_router.get("/me")
def get_me(user: User = Depends(current_user)):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "credits": user.credits,
        "role": user.role,
        "vendor_id": user.vendor_id,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "expiry_date": user.expiry_date.isoformat() if user.expiry_date else None,
    }

@users_router.post("/change-password")
def change_password(
    body: ChangePasswordReq,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    if not verify_pw(body.current_password, user.password_hash):
        raise HTTPException(400, "Current password is incorrect")
    if len(body.new_password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters")
    user.password_hash = hash_pw(body.new_password)
    db.commit()
    return {"message": "Password changed successfully"}
