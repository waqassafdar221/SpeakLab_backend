from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from pydantic_settings import BaseSettings

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./dev.db"
    MEDIA_DIR: str = "./media"
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
