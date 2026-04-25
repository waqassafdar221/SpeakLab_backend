import os
import httpx
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter(prefix="/transcription", tags=["transcription"])

GROQ_API_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB

# Maps extension → MIME type accepted by Groq Whisper
EXT_MIME = {
    ".flac": "audio/flac",
    ".mp3":  "audio/mpeg",
    ".mp4":  "audio/mp4",
    ".m4a":  "audio/mp4",
    ".ogg":  "audio/ogg",
    ".opus": "audio/ogg",
    ".wav":  "audio/wav",
    ".webm": "audio/webm",
    ".mpeg": "audio/mpeg",
    ".mpga": "audio/mpeg",
}


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Public demo endpoint for audio transcription using Groq Whisper API."""
    groq_api_key = os.getenv("GROQ_API_KEY", "")
    if not groq_api_key:
        raise HTTPException(500, "Groq API key not configured")

    filename = file.filename or "audio.webm"
    ext = os.path.splitext(filename)[1].lower()
    if not ext:
        ext = ".webm"
        filename = f"audio{ext}"

    if ext not in EXT_MIME:
        raise HTTPException(
            400,
            f"Unsupported format. Supported: {', '.join(sorted(EXT_MIME))}",
        )

    file_content = await file.read()

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large. Maximum size is 25MB.")

    if len(file_content) == 0:
        raise HTTPException(400, "Audio file is empty.")

    # Always use extension-derived MIME type — browser content_type can
    # include codec params (e.g. "audio/webm;codecs=opus") that Groq rejects.
    content_type = EXT_MIME[ext]

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(
                GROQ_API_URL,
                headers={"Authorization": f"Bearer {groq_api_key}"},
                files={"file": (filename, file_content, content_type)},
                data={"model": "whisper-large-v3", "response_format": "verbose_json"},
            )

            if response.status_code != 200:
                error_msg = "Transcription failed"
                try:
                    error_msg = response.json().get("error", {}).get("message", error_msg)
                except Exception:
                    pass
                raise HTTPException(500, f"Groq API error: {error_msg}")

            result = response.json()
            return {
                "text": result.get("text", ""),
                "language": result.get("language", "unknown"),
                "duration": round(result.get("duration", 0), 1),
            }

    except httpx.TimeoutException:
        raise HTTPException(504, "Transcription timed out. Please try a shorter audio file.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Transcription failed: {str(e)}")
