import os, uuid, wave, struct, httpx
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db, settings as app_settings
from ..models import User, Voice, Job
from ..schemas import TTSReq
from ..deps import current_user

from ..providers.edge_tts_provider import EdgeTTSProvider

router = APIRouter(prefix="/tts", tags=["tts"])
MEDIA_DIR = app_settings.MEDIA_DIR
os.makedirs(MEDIA_DIR, exist_ok=True)

EXTERNAL_TTS_API = "https://corrine-storiated-salma.ngrok-free.dev/tts"

_provider = None
def provider():
    global _provider
    if _provider is None:
        _provider = EdgeTTSProvider()  # default en_us_jenny
    return _provider

@router.post("/generate")
async def generate(body: TTSReq, db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Generate speech audio using cloned voice or Edge TTS.

    Takes either a public voice key (from /voices/public) or a user's saved voice_id.
    Charges 1 credit per character.
    """
    text = (body.text or "").strip()
    if not text:
        raise HTTPException(400, "Text is required")

    # Determine if using cloned voice or public voice
    use_cloned_voice = False
    reference_audio_filename = None
    
    if body.voice_id is not None:
        v = db.get(Voice, body.voice_id)
        if not v or v.user_id != user.id:
            raise HTTPException(404, "Voice not found")
        
        if v.is_cloned:
            use_cloned_voice = True
            reference_audio_filename = v.provider_voice_id
        else:
            raise HTTPException(400, "Voice is not a cloned voice")

    # Estimate and charge credits
    cost = len(text)  # 1 credit per character
    if user.credits < cost:
        raise HTTPException(402, "Not enough credits")
    user.credits -= cost
    db.add(user)  # mark dirty

    # Create job row
    job = Job(user_id=user.id, job_type="tts", input_text=text, voice_id=body.voice_id, status="processing", cost=cost)
    db.add(job); db.commit(); db.refresh(job)

    # Synthesize audio
    try:
        if use_cloned_voice:
            # Use external TTS API for cloned voices
            async with httpx.AsyncClient(timeout=120.0) as client:
                payload = {
                    "text": text,
                    "voice_mode": "predefined",
                    "predefined_voice_id": reference_audio_filename,
                    "output_format": "wav"
                }
                print(f"Sending TTS request with payload: {payload}")
                response = await client.post(EXTERNAL_TTS_API, json=payload)
                
                if response.status_code != 200:
                    error_detail = response.text
                    print(f"TTS API error: {response.status_code} - {error_detail}")
                    raise HTTPException(500, f"TTS API error ({response.status_code}): {error_detail}")
                
                audio_bytes = response.content
                ext = "wav"
        else:
            # Use Edge TTS for public voices
            audio_bytes, ext = await provider().synthesize(text, public_voice_key=body.public_voice)
    except httpx.HTTPStatusError as e:
        job.status = "error"
        db.commit()
        error_detail = e.response.text if hasattr(e.response, 'text') else str(e)
        print(f"HTTP error: {error_detail}")
        raise HTTPException(500, f"TTS API error: {error_detail}")
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
