from datetime import datetime, timedelta
from jose import jwt
from passlib.hash import pbkdf2_sha256
from .db import settings as S

def hash_pw(pw: str) -> str:
    # pbkdf2_sha256 is pure-Python and cross-platform; no 72-byte limit issues
    return pbkdf2_sha256.hash(pw)

def verify_pw(pw: str, ph: str) -> bool:
    return pbkdf2_sha256.verify(pw, ph)

def make_token(username: str, role: str, minutes: int = 60*24):
    payload = {"sub": username, "role": role, "exp": datetime.utcnow() + timedelta(minutes=minutes)}
    return jwt.encode(payload, S.jwt_secret, algorithm=S.jwt_algo)
