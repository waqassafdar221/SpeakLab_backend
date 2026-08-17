from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/postgres"
    MEDIA_DIR: str = "/tmp/media" if os.getenv("VERCEL") else "./media"
    MEDIA_STORAGE: str = "r2" if os.getenv("VERCEL") else "local"  # local | r2
    R2_ENDPOINT_URL: str = "https://d37ae443348786f63a7cde59db69f9a2.r2.cloudflarestorage.com/speaklab-media"
    R2_BUCKET_NAME: str = "speaklab-media"
    R2_PUBLIC_BASE_URL: str = "https://d37ae443348786f63a7cde59db69f9a2.r2.cloudflarestorage.com/speaklab-media"
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    jwt_secret: str = "change_me"
    jwt_algo: str = "HS256"
    hf_api_key: str = ""
    GROQ_API_KEY: str = ""
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""
    FRONTEND_BASE_URL: str = "http://localhost:3000"
    CRON_SECRET: str = ""
    LOW_CREDIT_THRESHOLD: int = 50
    EXPIRY_WARNING_DAYS: int = 3

    class Config:
        env_file = ".env"


settings = Settings()

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase): pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_role_columns():
    """Additive migration: add users.role / users.vendor_id if this table
    predates the vendor tier, and backfill role from the old is_admin flag.
    Never drops or renames columns — this runs against the live database."""
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return  # fresh database; create_all() will create the current schema

    column_info = {col["name"]: col for col in inspector.get_columns("users")}
    with engine.begin() as conn:
        if "role" not in column_info:
            conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20)"))
            if "is_admin" in column_info:
                conn.execute(text(
                    "UPDATE users SET role = CASE WHEN is_admin THEN 'admin' ELSE 'customer' END"
                ))
            else:
                conn.execute(text("UPDATE users SET role = 'customer' WHERE role IS NULL"))
        if "vendor_id" not in column_info:
            conn.execute(text("ALTER TABLE users ADD COLUMN vendor_id INTEGER REFERENCES users(id)"))
        # is_admin is no longer written by the app (superseded by role); relax its
        # NOT NULL constraint so new inserts don't have to fake a value for it.
        if "is_admin" in column_info and not column_info["is_admin"]["nullable"] and engine.dialect.name == "postgresql":
            conn.execute(text("ALTER TABLE users ALTER COLUMN is_admin DROP NOT NULL"))
        if "invite_token" not in column_info:
            conn.execute(text("ALTER TABLE users ADD COLUMN invite_token VARCHAR(64)"))
        if "invite_expires_at" not in column_info:
            conn.execute(text("ALTER TABLE users ADD COLUMN invite_expires_at TIMESTAMP WITH TIME ZONE"))
        if "reset_token" not in column_info:
            conn.execute(text("ALTER TABLE users ADD COLUMN reset_token VARCHAR(64)"))
        if "reset_expires_at" not in column_info:
            conn.execute(text("ALTER TABLE users ADD COLUMN reset_expires_at TIMESTAMP WITH TIME ZONE"))
        if "low_credit_notified_at" not in column_info:
            conn.execute(text("ALTER TABLE users ADD COLUMN low_credit_notified_at TIMESTAMP WITH TIME ZONE"))
        if "expiry_notified_at" not in column_info:
            conn.execute(text("ALTER TABLE users ADD COLUMN expiry_notified_at TIMESTAMP WITH TIME ZONE"))
        if "monthly_price" not in column_info:
            conn.execute(text("ALTER TABLE users ADD COLUMN monthly_price DOUBLE PRECISION DEFAULT 0"))
            conn.execute(text("UPDATE users SET monthly_price = 0 WHERE monthly_price IS NULL"))


def ensure_audit_log_fk():
    """audit_logs.actor_id must not block deleting a user who has ever
    performed a logged action — the log already keeps actor_username as a
    snapshot, so the row should survive with actor_id set to NULL instead."""
    inspector = inspect(engine)
    if "audit_logs" not in inspector.get_table_names() or engine.dialect.name != "postgresql":
        return
    for fk in inspector.get_foreign_keys("audit_logs"):
        if fk["constrained_columns"] == ["actor_id"] and fk.get("options", {}).get("ondelete") != "SET NULL":
            with engine.begin() as conn:
                conn.execute(text(f'ALTER TABLE audit_logs DROP CONSTRAINT "{fk["name"]}"'))
                conn.execute(text(
                    "ALTER TABLE audit_logs ADD CONSTRAINT audit_logs_actor_id_fkey "
                    "FOREIGN KEY (actor_id) REFERENCES users(id) ON DELETE SET NULL"
                ))
