from typing import Literal
from pydantic import BaseModel, EmailStr, Field

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
    role: Literal["vendor", "customer"] = "customer"
    package_id: int | None = None
    initial_credits: int = 0


class CreateCustomerReq(BaseModel):
    username: str
    email: EmailStr
    package_id: int | None = None
    initial_credits: int = 0


class SetPasswordReq(BaseModel):
    token: str
    password: str

class TTSReq(BaseModel):
    text: str
    public_voice: str | None = None
    speed: float | None = Field(default=1.0, ge=0.5, le=2.0)
    pitch: int | None = Field(default=0, ge=-50, le=50)
    volume: float | None = Field(default=1.0, ge=0.0, le=2.0)

class ChangePasswordReq(BaseModel):
    current_password: str
    new_password: str

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
