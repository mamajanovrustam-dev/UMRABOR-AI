"""Схемы пакетов / вылетов / инвентаря."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import ModerationDecision, PackageStatus, RoomType
from app.schemas.common import TimestampedSchema


class HotelInPackage(BaseModel):
    hotel_id: UUID
    nights: int = Field(ge=1)
    sort_order: int = 0


class HotelInPackageOut(BaseModel):
    id: UUID
    hotel_id: UUID
    hotel_name: str
    hotel_city: str
    hotel_stars: int
    nights: int
    sort_order: int


class DepartureInventoryIn(BaseModel):
    room_type: RoomType
    capacity: int = Field(ge=0)
    is_enabled: bool = True


class DepartureInventoryOut(BaseModel):
    id: UUID
    room_type: RoomType
    capacity: int
    sold: int
    is_enabled: bool

    model_config = {"from_attributes": True}


class DepartureIn(BaseModel):
    date_out: date
    date_in: date
    flight_out: str | None = None
    flight_in: str | None = None
    aircraft: str | None = None
    baggage: str | None = None
    price_sgl: int | None = None
    price_dbl: int | None = None
    price_trpl: int | None = None
    price_quad: int | None = None
    inventory: list[DepartureInventoryIn] = Field(default_factory=list)
    is_active: bool = True


class DepartureOut(TimestampedSchema):
    package_id: UUID
    date_out: date
    date_in: date
    flight_out: str | None = None
    flight_in: str | None = None
    aircraft: str | None = None
    baggage: str | None = None
    capacity_total: int
    sold_total: int
    price_sgl: int | None = None
    price_dbl: int | None = None
    price_trpl: int | None = None
    price_quad: int | None = None
    is_active: bool
    inventory: list[DepartureInventoryOut] = []


class PackageBase(BaseModel):
    name: str
    slug: str
    package_type_id: UUID | None = None
    airline_id: UUID | None = None
    transfer_type_id: UUID | None = None
    meal_type_id: UUID | None = None
    route: list[str] = Field(default_factory=list)
    duration_days: int = Field(ge=1)
    description: str | None = None
    photos: list[str] = Field(default_factory=list)
    price_sgl: int | None = None
    price_dbl: int | None = None
    price_trpl: int | None = None
    price_quad: int | None = None


class PackageCreate(PackageBase):
    hotels: list[HotelInPackage] = Field(default_factory=list)
    service_ids: list[UUID] = Field(default_factory=list)
    gift_ids: list[UUID] = Field(default_factory=list)


class PackageUpdate(PackageCreate):
    pass


class PackageOut(TimestampedSchema, PackageBase):
    partner_id: UUID
    partner_brand: str | None = None
    status: PackageStatus
    submitted_at: datetime | None = None
    moderated_at: datetime | None = None
    moderation_note: str | None = None
    hotels: list[HotelInPackageOut] = []
    service_ids: list[UUID] = []
    gift_ids: list[UUID] = []
    departures_count: int = 0
    sold_total: int = 0


class PackageDetailOut(PackageOut):
    departures: list[DepartureOut] = []


class PackageModerationIn(BaseModel):
    decision: ModerationDecision
    comment: str | None = None


class PackageSubmitIn(BaseModel):
    """Партнёр отправляет на модерацию."""
    note: str | None = None
