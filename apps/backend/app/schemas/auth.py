from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import BloodType, UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    role: UserRole
    donor_id: UUID | None = None
    hospital_id: UUID | None = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    refresh_token: str
    refresh_expires_at: datetime
    user: UserRead


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=16, max_length=2048)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(min_length=16, max_length=2048)


class DonorRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=150)
    phone: str = Field(min_length=6, max_length=30)
    date_of_birth: date
    blood_type: BloodType
    medical_history: str | None = None


class HospitalRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=2, max_length=200)
    address: str = Field(min_length=5)
    city: str = Field(min_length=2, max_length=100)
    latitude: float | None = None
    longitude: float | None = None
    contact_phone: str = Field(min_length=6, max_length=30)


class AdminRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class AuthMessage(BaseModel):
    message: str
    user: UserRead


class AuthStatus(BaseModel):
    message: str
