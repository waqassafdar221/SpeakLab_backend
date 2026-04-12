from pydantic import BaseModel, EmailStr

class LoginReq(BaseModel):
    username: str
    password: str

class TokenResp(BaseModel):
    access_token: str
    token_type: str = "bearer"

class PackageReq(BaseModel):
    name: str
    credits_per_period: int = 100
    demo_char_limit: int = 500

class CreateUserReq(BaseModel):
    username: str
    email: EmailStr
    password: str
    package_id: int | None = None
    initial_credits: int = 0

class TTSReq(BaseModel):
    text: str
    public_voice: str | None = None

class CreateClonedVoiceReq(BaseModel):
    name: str
    gender: str
    provider_voice_id: str
    status: str = "Ready"

class ClonedVoiceResp(BaseModel):
    id: int
    name: str
    gender: str | None
    status: str
    created_at: str
    provider_voice_id: str

    class Config:
        from_attributes = True
