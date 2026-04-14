from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Vercel serverless functions can only write to /tmp
    DATABASE_URL: str = "sqlite:////tmp/dev.db" if os.getenv("VERCEL") else "sqlite:///./dev.db"
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
