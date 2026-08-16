from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from datetime import datetime
from .db import get_db, settings as S
from .models import User

auth_scheme = HTTPBearer(auto_error=True)

def current_user(
    credentials: HTTPAuthorizationCredentials = Security(auth_scheme),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    try:
        data = jwt.decode(token, S.jwt_secret, algorithms=[S.jwt_algo])
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
    if user.role != "admin":
        raise HTTPException(403, "Admin only")
    return user


def require_vendor(user: User = Depends(current_user)):
    if user.role != "vendor":
        raise HTTPException(403, "Vendor only")
    return user
