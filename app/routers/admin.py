from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..db import get_db
from ..models import User, Package
from ..schemas import PackageReq, CreateUserReq
from ..deps import require_admin
from ..auth import hash_pw

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/packages")
def create_package(body: PackageReq, db: Session = Depends(get_db), _=Depends(require_admin)):
    if db.query(Package).filter_by(name=body.name).first():
        raise HTTPException(400, "Package name exists")
    p = Package(name=body.name, credits_per_period=body.credits_per_period, demo_char_limit=body.demo_char_limit)
    db.add(p); db.commit(); db.refresh(p)
    return {"id": p.id, "name": p.name}

@router.get("/packages")
def list_packages(db: Session = Depends(get_db), _=Depends(require_admin)):
    packages = db.query(Package).all()
    return [{"id": p.id, "name": p.name, "credits_per_period": p.credits_per_period, "demo_char_limit": p.demo_char_limit} for p in packages]

@router.post("/users")
def create_user(body: CreateUserReq, db: Session = Depends(get_db), _=Depends(require_admin)):
    if db.query(User).filter((User.username == body.username) | (User.email == body.email)).first():
        raise HTTPException(400, "Username or email exists")
    u = User(
        username=body.username,
        email=body.email,
        password_hash=hash_pw(body.password),
        is_admin=False,
        credits=body.initial_credits,
        package_id=body.package_id,
        expiry_date=datetime.now() + timedelta(days=30)
    )
    db.add(u); db.commit(); db.refresh(u)
    return {"id": u.id, "username": u.username}

@router.get("/users")
def list_users(db: Session = Depends(get_db), _=Depends(require_admin)):
    users = db.query(User).all()
    return [{
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "credits": u.credits,
        "is_admin": u.is_admin,
        "package_id": u.package_id,
        "created_at": u.created_at.isoformat() if u.created_at else None,
        "expiry_date": u.expiry_date.isoformat() if u.expiry_date else None
    } for u in users]

@router.get("/stats")
def get_stats(db: Session = Depends(get_db), _=Depends(require_admin)):
    total_users = db.query(User).count()
    total_credits = db.query(User).with_entities(User.credits).all()
    total_credits_sum = sum([u.credits for u in total_credits])
    
    # Count expired users
    now = datetime.now()
    expired_users = db.query(User).filter(
        User.expiry_date != None,
        User.expiry_date < now
    ).count()
    
    return {
        "total_users": total_users,
        "total_credits_allocated": total_credits_sum,
        "expired_users": expired_users
    }

@router.patch("/users/{user_id}/credits")
def update_user_credits(user_id: int, credits: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(404, "User not found")
    u.credits = credits
    db.commit()
    return {"id": u.id, "username": u.username, "credits": u.credits}

@router.patch("/users/{user_id}/extend-expiry")
def extend_user_expiry(user_id: int, days: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(404, "User not found")
    
    # If user has an expiry date, extend it, otherwise set from now
    if u.expiry_date:
        u.expiry_date = u.expiry_date + timedelta(days=days)
    else:
        u.expiry_date = datetime.now() + timedelta(days=days)
    
    db.commit()
    return {
        "id": u.id,
        "username": u.username,
        "expiry_date": u.expiry_date.isoformat() if u.expiry_date else None
    }

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(404, "User not found")
    if u.is_admin:
        raise HTTPException(400, "Cannot delete admin user")
    db.delete(u)
    db.commit()
    return {"message": "User deleted successfully"}

@router.post("/expire-credits")
def expire_all_credits(db: Session = Depends(get_db), _=Depends(require_admin)):
    """Check all users and expire credits for those whose expiry_date has passed"""
    now = datetime.now()
    expired_users = db.query(User).filter(
        User.expiry_date != None,
        User.expiry_date < now,
        User.credits > 0
    ).all()
    
    expired_count = 0
    for u in expired_users:
        u.credits = 0
        expired_count += 1
    
    db.commit()
    return {
        "message": f"Expired credits for {expired_count} users",
        "expired_count": expired_count
    }