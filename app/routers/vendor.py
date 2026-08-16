from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from datetime import datetime, timedelta
from ..db import get_db
from ..models import User, Job, Package
from ..schemas import CreateCustomerReq
from ..deps import require_vendor
from ..crud import create_user_row

router = APIRouter(prefix="/vendor", tags=["vendor"])


@router.get("/packages")
def list_packages(db: Session = Depends(get_db), vendor: User = Depends(require_vendor)):
    """Read-only: package plans are configured by the admin; vendors pick from the same list."""
    packages = db.query(Package).all()
    return [{
        "id": p.id,
        "name": p.name,
        "credits_per_period": p.credits_per_period,
        "demo_char_limit": p.demo_char_limit,
    } for p in packages]


def _get_own_customer(db: Session, vendor: User, customer_id: int) -> User:
    u = db.get(User, customer_id)
    if not u or u.vendor_id != vendor.id:
        raise HTTPException(404, "Customer not found")
    return u


@router.post("/customers")
def create_customer(body: CreateCustomerReq, db: Session = Depends(get_db), vendor: User = Depends(require_vendor)):
    u = create_user_row(
        db,
        username=body.username,
        email=body.email,
        password=body.password,
        role="customer",
        vendor_id=vendor.id,
        package_id=body.package_id,
        initial_credits=body.initial_credits,
    )
    return {"id": u.id, "username": u.username}


@router.get("/customers")
def list_customers(db: Session = Depends(get_db), vendor: User = Depends(require_vendor)):
    customers = db.query(User).filter(User.vendor_id == vendor.id).all()
    return [{
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "credits": u.credits,
        "package_id": u.package_id,
        "created_at": u.created_at.isoformat() if u.created_at else None,
        "expiry_date": u.expiry_date.isoformat() if u.expiry_date else None,
    } for u in customers]


@router.get("/stats")
def get_stats(db: Session = Depends(get_db), vendor: User = Depends(require_vendor)):
    base = db.query(User).filter(User.vendor_id == vendor.id)
    total_customers = base.count()
    total_credits = sum(u.credits for u in base.with_entities(User.credits).all())

    now = datetime.now()
    expired_customers = base.filter(User.expiry_date != None, User.expiry_date < now).count()

    return {
        "total_users": total_customers,
        "total_credits_allocated": total_credits,
        "expired_users": expired_customers,
    }


@router.patch("/customers/{customer_id}/credits")
def update_customer_credits(customer_id: int, credits: int, db: Session = Depends(get_db), vendor: User = Depends(require_vendor)):
    u = _get_own_customer(db, vendor, customer_id)
    u.credits = credits
    db.commit()
    return {"id": u.id, "username": u.username, "credits": u.credits}


@router.patch("/customers/{customer_id}/extend-expiry")
def extend_customer_expiry(customer_id: int, days: int, db: Session = Depends(get_db), vendor: User = Depends(require_vendor)):
    u = _get_own_customer(db, vendor, customer_id)
    if u.expiry_date:
        u.expiry_date = u.expiry_date + timedelta(days=days)
    else:
        u.expiry_date = datetime.now() + timedelta(days=days)
    db.commit()
    return {
        "id": u.id,
        "username": u.username,
        "expiry_date": u.expiry_date.isoformat() if u.expiry_date else None,
    }


@router.delete("/customers/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db), vendor: User = Depends(require_vendor)):
    u = _get_own_customer(db, vendor, customer_id)
    db.delete(u)
    db.commit()
    return {"message": "Customer deleted successfully"}


@router.get("/analytics/customers-growth")
def customers_growth(db: Session = Depends(get_db), vendor: User = Depends(require_vendor)):
    since = datetime.now() - timedelta(days=29)
    rows = (
        db.query(cast(User.created_at, Date).label("day"), func.count(User.id).label("count"))
        .filter(User.vendor_id == vendor.id, User.created_at >= since)
        .group_by(cast(User.created_at, Date))
        .order_by(cast(User.created_at, Date))
        .all()
    )
    result = {}
    for i in range(30):
        d = (since + timedelta(days=i)).date() if isinstance(since, datetime) else since + timedelta(days=i)
        result[str(d)] = 0
    for row in rows:
        result[str(row.day)] = row.count
    return [{"date": k, "count": v} for k, v in sorted(result.items())]


@router.get("/analytics/jobs-usage")
def jobs_usage(db: Session = Depends(get_db), vendor: User = Depends(require_vendor)):
    since = datetime.now() - timedelta(days=29)
    rows = (
        db.query(
            cast(Job.created_at, Date).label("day"),
            func.count(Job.id).label("jobs"),
            func.coalesce(func.sum(Job.cost), 0).label("credits"),
        )
        .join(User, Job.user_id == User.id)
        .filter(User.vendor_id == vendor.id, Job.created_at >= since, Job.job_type == "tts")
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
