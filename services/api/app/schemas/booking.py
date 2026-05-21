"""Схемы заявок."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import BookingSource, BookingStatus, RoomType
from app.schemas.common import TimestampedSchema


class PilgrimMini(BaseModel):
    id: UUID
    full_name: str
    gender: str
    document_type: str
    document_series_number: str | None = None
    has_mahram: bool = False
    mahram_id: UUID | None = None
    mahram_name: str | None = None
    mahram_relation: str | None = None

    model_config = {"from_attributes": True}


class PlacementOut(BaseModel):
    id: UUID
    room_type: RoomType
    capacity: int
    price_per_person_uzs: int
    total_uzs: int
    awaiting_co_lodger: bool
    pilgrim_ids: list[UUID] = []

    model_config = {"from_attributes": True}


class PlacementIn(BaseModel):
    room_type: RoomType
    pilgrim_ids: list[UUID] = Field(default_factory=list, min_length=1)


class BookingCreate(BaseModel):
    package_id: UUID
    departure_id: UUID
    pilgrim_ids: list[UUID] = Field(min_length=1)
    placements: list[PlacementIn] = Field(min_length=1)
    source: BookingSource = BookingSource.WEB


class BookingEventOut(BaseModel):
    id: UUID
    event_type: str
    title: str
    description: str | None = None
    actor_kind: str | None = None
    actor_name: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class BookingOut(TimestampedSchema):
    code: str
    partner_id: UUID
    partner_brand: str | None = None
    customer_id: UUID
    customer_name: str | None = None
    customer_phone: str | None = None
    package_id: UUID
    package_name: str | None = None
    departure_id: UUID
    departure_date_out: date | None = None
    departure_date_in: date | None = None
    source: BookingSource
    click_id: str | None = None
    status: BookingStatus
    sla_deadline_at: datetime | None = None
    total_uzs: int
    cashback_uzs: int
    confirmed_at: datetime | None = None
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None
    voucher_url: str | None = None


class BookingDetailOut(BookingOut):
    pilgrims: list[PilgrimMini] = []
    placements: list[PlacementOut] = []
    events: list[BookingEventOut] = []


class BookingRejectIn(BaseModel):
    reason_id: UUID | None = None
    comment: str | None = None
