from fastapi import APIRouter
from ..providers.edge_tts_provider import EdgeTTSProvider

router = APIRouter(prefix="/voices", tags=["voices"])

@router.get("/public")
def list_public_voices():
    return EdgeTTSProvider.public_voices()