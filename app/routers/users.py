from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User
from ..schemas import LoginReq, TokenResp, ChangePasswordReq
from ..auth import verify_pw, hash_pw, make_token
from ..deps import current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResp)
def login(body: LoginReq, db: Session = Depends(get_db)):
    identifier = (body.username or "").strip()
    u = db.query(User).filter(
        (User.username == identifier) | (User.email == identifier)
    ).first()
    if not u or not verify_pw(body.password, u.password_hash):
        raise HTTPException(401, "Invalid credentials")
    return TokenResp(access_token=make_token(u.username, u.is_admin))

users_router = APIRouter(prefix="/users", tags=["users"])

@users_router.get("/me")
def get_me(user: User = Depends(current_user)):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "credits": user.credits,
        "is_admin": user.is_admin,
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
