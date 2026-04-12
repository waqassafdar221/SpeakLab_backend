import sys
from .db import SessionLocal
from .models import User
from .auth import hash_pw


def main():
    if len(sys.argv) < 4:
        print("Usage: python -m app.bootstrap_admin <username> <email> <password>")
        sys.exit(1)
    username, email, password = sys.argv[1:4]
    db = SessionLocal()
    try:
        if db.query(User).filter((User.username == username) | (User.email == email)).first():
            print("User with that username or email already exists")
            return
        u = User(username=username, email=email, password_hash=hash_pw(password), is_admin=True, credits=10000)
        db.add(u); db.commit()
        print(f"Admin user created: {u.username}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
