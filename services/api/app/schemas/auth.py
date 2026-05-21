"""Схемы аутентификации для трёх типов субъектов."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import PartnerRole, UmraborRole


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # access TTL in seconds


# ─── UMRABOR ───
class UmraborLoginIn(BaseModel):
    login: str = Field(min_length=2, max_length=64)
    password: str = Field(min_length=1, max_length=200)


class UmraborMe(BaseModel):
    id: UUID
    login: str
    full_name: str
    email: str | None = None
    phone: str | None = None
    role: UmraborRole
    is_active: bool
    last_login_at: datetime | None = None


class UmraborLoginOut(BaseModel):
    tokens: TokenPair
    user: UmraborMe


# ─── Партнёр ───
class PartnerLoginIn(BaseModel):
    login: str = Field(min_length=2, max_length=64)
    password: str = Field(min_length=1, max_length=200)


class PartnerMe(BaseModel):
    id: UUID
    partner_id: UUID
    partner_brand: str
    login: str
    full_name: str
    email: str | None = None
    phone: str | None = None
    role: PartnerRole
    is_active: bool
    must_change_password: bool
    last_login_at: datetime | None = None


class PartnerLoginOut(BaseModel):
    tokens: TokenPair
    user: PartnerMe


class PartnerChangePasswordIn(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8, max_length=200)


# ─── Клиент ───
class CustomerOtpRequestIn(BaseModel):
    phone: str = Field(pattern=r"^\+998\d{9}$")


class CustomerOtpRequestOut(BaseModel):
    sent: bool = True
    debug_code: str | None = None  # только в development


class CustomerOtpVerifyIn(BaseModel):
    phone: str = Field(pattern=r"^\+998\d{9}$")
    code: str = Field(min_length=4, max_length=6)


class CustomerClickAuthIn(BaseModel):
    click_user_id: str = Field(min_length=1, max_length=64)
    phone: str = Field(pattern=r"^\+998\d{9}$")
    full_name: str | None = None
    email: EmailStr | None = None


class CustomerMe(BaseModel):
    id: UUID
    phone: str
    email: str | None = None
    full_name: str | None = None
    avatar_url: str | None = None


class CustomerLoginOut(BaseModel):
    tokens: TokenPair
    user: CustomerMe
    is_new: bool = False


# ─── Общие ───
class RefreshIn(BaseModel):
    refresh_token: str
