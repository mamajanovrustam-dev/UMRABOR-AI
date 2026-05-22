"""Схемы партнёров."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import PartnerRole, PartnerStatus
from app.schemas.common import TimestampedSchema


class PartnerBase(BaseModel):
    legal_name: str
    brand: str
    slug: str
    city: str
    founded_year: int | None = None
    logo_url: str | None = None

    license_no: str | None = None
    license_authority: str = "Госкомтуризм РУз"
    license_issued_at: date | None = None
    license_until: date | None = None
    license_file_url: str | None = None

    inn: str | None = None
    oked: str | None = None
    bank_account: str | None = None
    bank_name: str | None = None
    bank_mfo: str | None = None
    vat_code: str | None = None
    legal_address: str | None = None
    actual_address: str | None = None

    contact_full_name: str | None = None
    contact_position: str | None = None
    contact_phone: str | None = None
    contact_email: EmailStr | None = None

    internal_note: str | None = None


class PartnerCreate(PartnerBase):
    admin_first_name: str = Field(min_length=1, max_length=100)
    admin_last_name: str = Field(min_length=1, max_length=100)
    admin_login: str = Field(min_length=2, max_length=64)
    admin_password: str = Field(min_length=8, max_length=200)
    admin_phone: str | None = None
    admin_email: EmailStr | None = None


class PartnerUpdate(PartnerBase):
    pass


class PartnerOut(TimestampedSchema, PartnerBase):
    status: PartnerStatus
    status_changed_at: datetime | None = None


class PartnerStatusChangeIn(BaseModel):
    status: PartnerStatus
    reason: str | None = None


class PartnerStatusHistoryItem(BaseModel):
    id: UUID
    status: PartnerStatus
    reason: str | None = None
    changed_by_user_id: UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PartnerEmployeeOut(BaseModel):
    id: UUID
    partner_id: UUID
    login: str
    full_name: str
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    email: str | None = None
    role: PartnerRole
    is_active: bool
    must_change_password: bool
    last_login_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PartnerEmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    login: str = Field(min_length=2, max_length=64)
    phone: str | None = None
    email: EmailStr | None = None
    role: PartnerRole = PartnerRole.OPERATOR
    password: str = Field(min_length=8, max_length=200)


class PartnerEmployeeUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    role: PartnerRole | None = None
    is_active: bool | None = None
