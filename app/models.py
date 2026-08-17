from sqlalchemy import String, Integer, Boolean, Float, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

class Package(Base):
    __tablename__ = "packages"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    credits_per_period: Mapped[int] = mapped_column(Integer, default=100)
    demo_char_limit: Mapped[int] = mapped_column(Integer, default=500)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True)
    email: Mapped[str] = mapped_column(String(120), unique=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(20), default="customer")  # 'admin' | 'vendor' | 'customer'
    vendor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), default=None)
    vendor: Mapped["User | None"] = relationship(remote_side=[id], foreign_keys=[vendor_id])
    credits: Mapped[int] = mapped_column(Integer, default=0)
    package_id: Mapped[int | None] = mapped_column(ForeignKey("packages.id"))
    package: Mapped[Package | None] = relationship(backref="users")
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expiry_date: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), default=None)
    invite_token: Mapped[str | None] = mapped_column(String(64), default=None)
    invite_expires_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), default=None)
    reset_token: Mapped[str | None] = mapped_column(String(64), default=None)
    reset_expires_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), default=None)
    low_credit_notified_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), default=None)
    expiry_notified_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), default=None)
    monthly_price: Mapped[float] = mapped_column(Float, default=0)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    actor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    actor_username: Mapped[str] = mapped_column(String(80))
    action: Mapped[str] = mapped_column(String(50))
    target_type: Mapped[str | None] = mapped_column(String(30), default=None)
    target_id: Mapped[int | None] = mapped_column(Integer, default=None)
    target_username: Mapped[str | None] = mapped_column(String(80), default=None)
    details: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class Voice(Base):
    __tablename__ = "voices"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    provider_voice_id: Mapped[str] = mapped_column(String(200))
    name: Mapped[str] = mapped_column(String(100))
    is_cloned: Mapped[bool] = mapped_column(Boolean, default=True)
    gender: Mapped[str | None] = mapped_column(String(20), default=None)
    status: Mapped[str] = mapped_column(String(20), default="Ready")
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    job_type: Mapped[str] = mapped_column(String(30))  # 'tts' | 'clone'
    input_text: Mapped[str] = mapped_column(Text, default="")
    voice_id: Mapped[int | None] = mapped_column(ForeignKey("voices.id"))
    status: Mapped[str] = mapped_column(String(20), default="queued")
    cost: Mapped[int] = mapped_column(Integer, default=0)
    output_url: Mapped[str | None] = mapped_column(String(300))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
