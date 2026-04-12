from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from pydantic_settings import BaseSettings
from datetime import datetime
from .db import get_db
from .models import User

class Settings(BaseSettings):
    JWT_SECRET: str = "change_me"
    JWT_ALGO: str = "HS256"
    class Config: env_file = ".env"
S = Settings()
auth_scheme = HTTPBearer(auto_error=True)

def current_user(
    credentials: HTTPAuthorizationCredentials = Security(auth_scheme),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    try:
        data = jwt.decode(token, S.JWT_SECRET, algorithms=[S.JWT_ALGO])
        u = db.query(User).filter_by(username=data["sub"]).first()
        if not u: raise HTTPException(401, "User not found")
        
        # Check if account has expired and zero out credits if so
        if u.expiry_date and u.expiry_date < datetime.now(u.expiry_date.tzinfo):
            if u.credits > 0:
                u.credits = 0
                db.commit()
        
        return u
    except JWTError:
        raise HTTPException(401, "Invalid token")

def require_admin(user: User = Depends(current_user)):
    if not user.is_admin:
        raise HTTPException(403, "Admin only")
    return user
