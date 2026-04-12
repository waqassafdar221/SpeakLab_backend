from db import SessionLocal
from models import Ping

# quick runner to verify the root response logic without needing FastAPI

def run_check():
    db = SessionLocal()
    try:
        if not db.query(Ping).first():
            db.add(Ping(note="boot"))
            db.commit()
        row = db.query(Ping).first()
        print({"status": "ok", "db_note": row.note})
    finally:
        db.close()

if __name__ == '__main__':
    run_check()
