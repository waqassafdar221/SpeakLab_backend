# TTS MVP (Edge TTS)

A minimal FastAPI backend that generates speech using Microsoft's Edge TTS voices.

## Endpoints

- GET `/` – health
- GET `/voices/public` – list curated public voices keys
- POST `/auth/login` – obtain JWT token
- POST `/admin/packages` – create package (admin)
- POST `/admin/users` – create user (admin)
- POST `/tts/generate` – generate audio

Request body for `/tts/generate`:

```
{
  "text": "Hello world",
  "public_voice": "en_us_jenny",   # optional; see /voices/public
  "voice_id": 123                    # optional; your saved voice (overrides public_voice)
}
```

Response:

```
{
  "job_id": 1,
  "status": "done",
  "output_url": "/media/<file>.mp3",
  "deducted": 11
}
```

Notes:
- Cost is 1 credit per input character. Requests require an authenticated user with sufficient credits.
- If both `voice_id` and `public_voice` are provided, `voice_id` wins and its `provider_voice_id` is used directly.

## Quick start (Windows PowerShell)

1) Create and activate a virtual environment (optional but recommended):

```powershell
py -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2) Install dependencies:

```powershell
pip install -r requirements.txt
```

3) Run the server:

```powershell
uvicorn app.main:app --reload
```

4) Create an admin user and a normal user:
- Bootstrap an admin quickly:

```powershell
python -m app.bootstrap_admin admin admin@example.com MySecureP@ss
```

- Then login to get a token via `/auth/login` and use `/admin/users` to create regular users.

5) Generate speech:
- Acquire a token via `/auth/login` and include it as `Authorization: Bearer <token>`.
- Call `/tts/generate` with your text.

Media files are saved in `./media` and served under `/media`.
