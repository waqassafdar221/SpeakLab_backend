import os, uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db, settings as app_settings
from ..models import User, Job
from ..schemas import TTSReq
from ..deps import current_user

from ..providers.edge_tts_provider import EdgeTTSProvider

router = APIRouter(prefix="/tts", tags=["tts"])
MEDIA_DIR = app_settings.MEDIA_DIR
os.makedirs(MEDIA_DIR, exist_ok=True)

_provider = None
def provider():
    global _provider
    if _provider is None:
        _provider = EdgeTTSProvider()  # default en_us_jenny
    return _provider

@router.post("/generate")
async def generate(body: TTSReq, db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Generate speech audio using Edge TTS public voices.

    Charges 1 credit per character.
    """
    text = (body.text or "").strip()
    if not text:
        raise HTTPException(400, "Text is required")

    if not body.public_voice:
        raise HTTPException(400, "Public voice is required")

    # Estimate and charge credits
    cost = len(text)  # 1 credit per character
    if user.credits < cost:
        raise HTTPException(402, "Not enough credits")
    user.credits -= cost
    db.add(user)  # mark dirty

    # Create job row
    job = Job(user_id=user.id, job_type="tts", input_text=text, voice_id=None, status="processing", cost=cost)
    db.add(job); db.commit(); db.refresh(job)

    # Synthesize audio
    try:
        # Use Edge TTS for public voices
        audio_bytes, ext = await provider().synthesize(text, public_voice_key=body.public_voice)
    except Exception as e:
        job.status = "error"
        db.commit()
        print(f"Synthesis error: {str(e)}")
        raise HTTPException(500, f"Synthesis failed: {e}")

    # Persist to file
    fname = f"{uuid.uuid4()}.{ext}"
    fpath = os.path.join(MEDIA_DIR, fname)
    with open(fpath, "wb") as f:
        f.write(audio_bytes)

    # Complete job
    job.status = "done"
    job.output_url = f"/media/{os.path.basename(fname)}"
    job.completed_at = datetime.utcnow()
    db.commit()

    return {"job_id": job.id, "status": job.status, "output_url": job.output_url, "deducted": cost}

@router.post("/demo")
async def demo_generate(body: TTSReq):
    """Public demo endpoint for generating speech without authentication.
    
    Limited to 300 characters and only works with public voices.
    Does not deduct credits or create job records.
    """
    text = (body.text or "").strip()
    if not text:
        raise HTTPException(400, "Text is required")
    
    if len(text) > 300:
        raise HTTPException(400, "Demo is limited to 300 characters")
    
    if not body.public_voice:
        raise HTTPException(400, "Public voice is required for demo")

    # Synthesize audio using Edge TTS
    try:
        audio_bytes, ext = await provider().synthesize(text, public_voice_key=body.public_voice)
    except Exception as e:
        print(f"Demo synthesis error: {str(e)}")
        raise HTTPException(500, f"Synthesis failed: {e}")

    # Persist to file
    fname = f"demo_{uuid.uuid4()}.{ext}"
    fpath = os.path.join(MEDIA_DIR, fname)
    with open(fpath, "wb") as f:
        f.write(audio_bytes)

    return {"status": "done", "output_url": f"/media/{os.path.basename(fname)}"}
