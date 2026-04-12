from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .db import Base, engine, settings
from .routers import users, admin, tts, voices


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

# Routers
app.include_router(users.router)
app.include_router(users.users_router)
app.include_router(admin.router)
app.include_router(voices.router)
app.include_router(tts.router)

# Static serving for generated media
app.mount("/media", StaticFiles(directory=settings.MEDIA_DIR), name="media")

@app.get("/")
def health():
    return {"status": "ok"}
