from app.db import SessionLocal, Base, engine
from app.models import User, Package
from app.auth import hash_pw

# Idempotent seed: ensure tables, create default package and admin if missing
Base.metadata.create_all(engine)

def seed():
    db = SessionLocal()
    try:
        pkg = db.query(Package).filter_by(name="Starter").first()
        if not pkg:
            pkg = Package(name="Starter", credits_per_period=100, demo_char_limit=500)
            db.add(pkg); db.commit(); db.refresh(pkg)
        admin = db.query(User).filter_by(username="admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@example.com",
                password_hash=hash_pw("admin123"),
                is_admin=True,
                credits=0,
                package_id=pkg.id,
            )
            db.add(admin); db.commit()
        print({"status": "ok", "admin": admin.username, "package": pkg.name})
    finally:
        db.close()

if __name__ == "__main__":
    seed()
