from datetime import datetime, timedelta
from jose import jwt
from passlib.hash import pbkdf2_sha256
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    JWT_SECRET: str = "change_me"
    JWT_ALGO: str = "HS256"
    class Config: env_file = ".env"

S = Settings()

def hash_pw(pw: str) -> str:
    # pbkdf2_sha256 is pure-Python and cross-platform; no 72-byte limit issues
    return pbkdf2_sha256.hash(pw)

def verify_pw(pw: str, ph: str) -> bool:
    return pbkdf2_sha256.verify(pw, ph)

def make_token(username: str, is_admin: bool, minutes: int = 60*24):
    payload = {"sub": username, "adm": is_admin, "exp": datetime.utcnow() + timedelta(minutes=minutes)}
    return jwt.encode(payload, S.JWT_SECRET, algorithm=S.JWT_ALGO)
