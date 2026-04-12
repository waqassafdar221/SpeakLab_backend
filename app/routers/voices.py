from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..providers.edge_tts_provider import EdgeTTSProvider
from ..deps import current_user
from ..db import get_db
from ..models import Voice, User
from ..schemas import CreateClonedVoiceReq, ClonedVoiceResp
from typing import List

router = APIRouter(prefix="/voices", tags=["voices"])

@router.get("/public")
def list_public_voices():
    return EdgeTTSProvider.public_voices()

@router.get("/cloned", response_model=List[ClonedVoiceResp])
def list_cloned_voices(
    user: User = Depends(current_user),
    db: Session = Depends(get_db)
):
    """Get all cloned voices for the current user"""
    voices = db.query(Voice).filter(
        Voice.user_id == user.id,
        Voice.is_cloned == True
    ).all()
    
    return [
        ClonedVoiceResp(
            id=voice.id,
            name=voice.name,
            gender=voice.gender,
            status=voice.status,
            created_at=voice.created_at.isoformat(),
            provider_voice_id=voice.provider_voice_id
        )
        for voice in voices
    ]

@router.post("/cloned", response_model=ClonedVoiceResp)
def create_cloned_voice(
    voice_data: CreateClonedVoiceReq,
    user: User = Depends(current_user),
    db: Session = Depends(get_db)
):
    """Save a cloned voice for the current user"""
    new_voice = Voice(
        user_id=user.id,
        name=voice_data.name,
        gender=voice_data.gender,
        provider_voice_id=voice_data.provider_voice_id,
        is_cloned=True,
        status=voice_data.status
    )
    
    db.add(new_voice)
    db.commit()
    db.refresh(new_voice)
    
    return ClonedVoiceResp(
        id=new_voice.id,
        name=new_voice.name,
        gender=new_voice.gender,
        status=new_voice.status,
        created_at=new_voice.created_at.isoformat(),
        provider_voice_id=new_voice.provider_voice_id
    )