from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, cast, Date, or_
from datetime import datetime, timedelta, date
from ..db import get_db
from ..models import User, Package, Job, AuditLog
from ..schemas import PackageReq, CreateUserReq
from ..deps import require_admin
from ..crud import create_user_row
from ..email_service import send_invite_email
from ..audit import log_action

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/packages")
def create_package(body: PackageReq, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    if db.query(Package).filter_by(name=body.name).first():
        raise HTTPException(400, "Package name exists")
    p = Package(name=body.name, credits_per_period=body.credits_per_period, demo_char_limit=body.demo_char_limit)
    db.add(p); db.commit(); db.refresh(p)
    log_action(db, admin, "package.create", target_type="package", target_id=p.id, target_username=p.name)
    return {"id": p.id, "name": p.name}

@router.get("/packages")
def list_packages(db: Session = Depends(get_db), _=Depends(require_admin)):
    packages = db.query(Package).all()
    return [{"id": p.id, "name": p.name, "credits_per_period": p.credits_per_period, "demo_char_limit": p.demo_char_limit} for p in packages]

@router.post("/users")
def create_user(body: CreateUserReq, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    u = create_user_row(
        db,
        username=body.username,
        email=body.email,
        role=body.role,
        vendor_id=None,
        package_id=body.package_id,
        initial_credits=body.initial_credits,
        monthly_price=body.monthly_price,
    )
    email_sent = send_invite_email(u.email, u.username, u.invite_token)
    log_action(db, admin, f"{u.role}.create", target_type="user", target_id=u.id, target_username=u.username)
    return {"id": u.id, "username": u.username, "role": u.role, "email_sent": email_sent}

@router.get("/users")
def list_users(
    search: str = "",
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    Vendor = aliased(User)
    query = db.query(User, Vendor.username).outerjoin(Vendor, User.vendor_id == Vendor.id)
    if search:
        like = f"%{search}%"
        query = query.filter(or_(User.username.ilike(like), User.email.ilike(like)))
    total = query.count()
    rows = (
        query.order_by(User.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    items = [{
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "credits": u.credits,
        "role": u.role,
        "vendor_id": u.vendor_id,
        "vendor_username": vendor_username,
        "package_id": u.package_id,
        "monthly_price": u.monthly_price,
        "invite_pending": u.invite_token is not None,
        "created_at": u.created_at.isoformat() if u.created_at else None,
        "expiry_date": u.expiry_date.isoformat() if u.expiry_date else None
    } for u, vendor_username in rows]
    return {"items": items, "total": total, "page": page, "page_size": page_size}

@router.get("/audit-log")
def list_audit_log(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    query = db.query(AuditLog)
    total = query.count()
    rows = (
        query.order_by(AuditLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    items = [{
        "id": a.id,
        "actor_username": a.actor_username,
        "action": a.action,
        "target_type": a.target_type,
        "target_id": a.target_id,
        "target_username": a.target_username,
        "details": a.details,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    } for a in rows]
    return {"items": items, "total": total, "page": page, "page_size": page_size}

@router.get("/vendors")
def list_vendors(db: Session = Depends(get_db), _=Depends(require_admin)):
    Customer = aliased(User)
    rows = (
        db.query(User, func.count(Customer.id).label("customer_count"))
        .outerjoin(Customer, Customer.vendor_id == User.id)
        .filter(User.role == "vendor")
        .group_by(User.id)
        .order_by(User.created_at.desc())
        .all()
    )
    return [{
        "id": v.id,
        "username": v.username,
        "email": v.email,
        "customer_count": count,
        "created_at": v.created_at.isoformat() if v.created_at else None,
    } for v, count in rows]

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
def update_user_credits(user_id: int, credits: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(404, "User not found")
    old_credits = u.credits
    u.credits = credits
    db.commit()
    log_action(db, admin, "user.update_credits", target_type="user", target_id=u.id, target_username=u.username,
               details=f"{old_credits} -> {credits}")
    return {"id": u.id, "username": u.username, "credits": u.credits}

@router.patch("/users/{user_id}/price")
def update_user_price(user_id: int, monthly_price: float, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    if monthly_price < 0:
        raise HTTPException(400, "Price cannot be negative")
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(404, "User not found")
    old_price = u.monthly_price
    u.monthly_price = monthly_price
    db.commit()
    log_action(db, admin, "user.update_price", target_type="user", target_id=u.id, target_username=u.username,
               details=f"{old_price} -> {monthly_price}")
    return {"id": u.id, "username": u.username, "monthly_price": u.monthly_price}

@router.get("/revenue")
def get_revenue(db: Session = Depends(get_db), _=Depends(require_admin)):
    Customer = aliased(User)
    rows = (
        db.query(
            User,
            func.count(Customer.id).label("customer_count"),
            func.coalesce(func.sum(Customer.monthly_price), 0).label("customer_mrr"),
        )
        .outerjoin(Customer, Customer.vendor_id == User.id)
        .filter(User.role == "vendor")
        .group_by(User.id)
        .order_by(User.created_at.desc())
        .all()
    )
    vendor_mrr = sum(v.monthly_price for v, _, _ in rows)
    customer_mrr = sum(float(cm) for _, _, cm in rows)
    return {
        "vendor_mrr": vendor_mrr,
        "customer_mrr": customer_mrr,
        "vendors": [{
            "id": v.id,
            "username": v.username,
            "monthly_price": v.monthly_price,
            "customer_count": count,
            "customer_mrr": float(cm),
        } for v, count, cm in rows],
    }

@router.patch("/users/{user_id}/extend-expiry")
def extend_user_expiry(user_id: int, days: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(404, "User not found")

    # If user has an expiry date, extend it, otherwise set from now
    if u.expiry_date:
        u.expiry_date = u.expiry_date + timedelta(days=days)
    else:
        u.expiry_date = datetime.now() + timedelta(days=days)

    db.commit()
    log_action(db, admin, "user.extend_expiry", target_type="user", target_id=u.id, target_username=u.username,
               details=f"+{days} days")
    return {
        "id": u.id,
        "username": u.username,
        "expiry_date": u.expiry_date.isoformat() if u.expiry_date else None
    }

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(404, "User not found")
    if u.role == "admin":
        raise HTTPException(400, "Cannot delete admin user")
    if u.role == "vendor":
        customer_count = db.query(User).filter(User.vendor_id == u.id).count()
        if customer_count:
            raise HTTPException(400, f"Vendor has {customer_count} customers assigned, remove them first")
    deleted_username, deleted_role = u.username, u.role
    db.delete(u)
    db.commit()
    log_action(db, admin, f"{deleted_role}.delete", target_type="user", target_id=user_id, target_username=deleted_username)
    return {"message": "User deleted successfully"}

@router.get("/analytics/users-growth")
def users_growth(db: Session = Depends(get_db), _=Depends(require_admin)):
    since = datetime.now() - timedelta(days=29)
    rows = (
        db.query(cast(User.created_at, Date).label("day"), func.count(User.id).label("count"))
        .filter(User.created_at >= since)
        .group_by(cast(User.created_at, Date))
        .order_by(cast(User.created_at, Date))
        .all()
    )
    # Build full 30-day range with 0-fill for missing days
    result = {}
    for i in range(30):
        d = (since + timedelta(days=i)).date() if isinstance(since, datetime) else since + timedelta(days=i)
        result[str(d)] = 0
    for row in rows:
        result[str(row.day)] = row.count
    return [{"date": k, "count": v} for k, v in sorted(result.items())]


@router.get("/analytics/jobs-usage")
def jobs_usage(db: Session = Depends(get_db), _=Depends(require_admin)):
    since = datetime.now() - timedelta(days=29)
    rows = (
        db.query(
            cast(Job.created_at, Date).label("day"),
            func.count(Job.id).label("jobs"),
            func.coalesce(func.sum(Job.cost), 0).label("credits"),
        )
        .filter(Job.created_at >= since, Job.job_type == "tts")
        .group_by(cast(Job.created_at, Date))
        .order_by(cast(Job.created_at, Date))
        .all()
    )
    result: dict[str, dict] = {}
    for i in range(30):
        d = (since + timedelta(days=i)).date()
        result[str(d)] = {"jobs": 0, "credits": 0}
    for row in rows:
        result[str(row.day)] = {"jobs": row.jobs, "credits": int(row.credits)}
    return [{"date": k, "jobs": v["jobs"], "credits": v["credits"]} for k, v in sorted(result.items())]


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