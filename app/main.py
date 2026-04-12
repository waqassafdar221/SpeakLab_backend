from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from .db import Base, engine, settings
from .db import SessionLocal
from .routers import users, admin, tts, voices
from .models import User, Package
from .auth import hash_pw


app = FastAPI(title="TTS MVP")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(engine)


def ensure_bootstrap_admin():
    """Create admin user at startup when ADMIN_* env vars are provided."""
    admin_username = os.getenv("ADMIN_USERNAME")
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")

    # Skip silently unless all required env vars are configured
    if not (admin_username and admin_email and admin_password):
        return

    db = SessionLocal()
    try:
        existing = db.query(User).filter(
            (User.username == admin_username) | (User.email == admin_email)
        ).first()
        if existing:
            return

        pkg = db.query(Package).filter_by(name="Starter").first()
        if not pkg:
            pkg = Package(name="Starter", credits_per_period=100, demo_char_limit=500)
            db.add(pkg)
            db.commit()
            db.refresh(pkg)

        admin_credits = int(os.getenv("ADMIN_INITIAL_CREDITS", "10000"))
        u = User(
            username=admin_username,
            email=admin_email,
            password_hash=hash_pw(admin_password),
            is_admin=True,
            credits=admin_credits,
            package_id=pkg.id,
        )
        db.add(u)
        db.commit()
    finally:
        db.close()


ensure_bootstrap_admin()

# Routers
app.include_router(users.router)
app.include_router(users.users_router)
app.include_router(admin.router)
app.include_router(voices.router)
app.include_router(tts.router)

# Static serving for generated media
os.makedirs(settings.MEDIA_DIR, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.MEDIA_DIR), name="media")

@app.get("/")
def health():
    return {"status": "ok"}
