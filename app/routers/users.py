from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User
from ..schemas import LoginReq, TokenResp
from ..auth import verify_pw, make_token
from ..deps import current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResp)
def login(body: LoginReq, db: Session = Depends(get_db)):
    u = db.query(User).filter_by(username=body.username).first()
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
