import os
import importlib
from urllib.parse import urlparse

from .db import settings

try:
    boto3 = importlib.import_module("boto3")
except Exception:
    boto3 = None


def _normalize_endpoint_and_bucket(endpoint_url: str, bucket_name: str) -> tuple[str, str]:
    endpoint_url = (endpoint_url or "").strip().rstrip("/")
    bucket_name = (bucket_name or "").strip()

    if not endpoint_url:
        return "", bucket_name

    parsed = urlparse(endpoint_url)
    path_parts = [p for p in parsed.path.split("/") if p]

    if path_parts and not bucket_name:
        bucket_name = path_parts[0]

    if parsed.scheme and parsed.netloc:
        endpoint_url = f"{parsed.scheme}://{parsed.netloc}"

    return endpoint_url.rstrip("/"), bucket_name


def _content_type_for_ext(ext: str) -> str:
    ext = (ext or "").lower().lstrip(".")
    if ext == "wav":
        return "audio/wav"
    if ext == "ogg":
        return "audio/ogg"
    if ext == "flac":
        return "audio/flac"
    return "audio/mpeg"


def save_audio_output(audio_bytes: bytes, file_name: str, ext: str) -> str:
    storage_mode = (settings.MEDIA_STORAGE or "local").lower()

    endpoint_url, bucket_name = _normalize_endpoint_and_bucket(
        settings.R2_ENDPOINT_URL,
        settings.R2_BUCKET_NAME,
    )

    can_use_r2 = (
        storage_mode == "r2"
        and boto3 is not None
        and endpoint_url
        and bucket_name
        and settings.R2_ACCESS_KEY_ID
        and settings.R2_SECRET_ACCESS_KEY
    )

    if can_use_r2:
        s3 = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
            region_name="auto",
        )

        s3.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=audio_bytes,
            ContentType=_content_type_for_ext(ext),
        )

        public_base = (settings.R2_PUBLIC_BASE_URL or "").strip().rstrip("/")
        if not public_base:
            public_base = f"{endpoint_url}/{bucket_name}"

        return f"{public_base}/{file_name}"

    os.makedirs(settings.MEDIA_DIR, exist_ok=True)
    file_path = os.path.join(settings.MEDIA_DIR, file_name)
    with open(file_path, "wb") as f:
        f.write(audio_bytes)

    return f"/media/{file_name}"
