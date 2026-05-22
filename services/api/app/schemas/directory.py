"""Схемы справочников."""

from pydantic import BaseModel, Field

from app.models.enums import City, DirectoryStatus, GiftBrand, RoomType, ServiceCategory
from app.schemas.common import TimestampedSchema


# ─── Hotel ───
class HotelIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=1, max_length=200)
    city: City
    stars: int = Field(ge=1, le=5, default=5)
    distance_value: float | None = None
    distance_unit: str = "м"
    walk_minutes: int | None = None
    transport_minutes: int | None = None
    description: str | None = None
    address: str | None = None
    lat: float | None = None
    lng: float | None = None
    photos: list[str] = Field(default_factory=list)
    amenities: list[str] = Field(default_factory=list)
    status: DirectoryStatus = DirectoryStatus.ACTIVE


class HotelOut(TimestampedSchema):
    name: str
    slug: str
    city: City
    stars: int
    distance_value: float | None = None
    distance_unit: str
    walk_minutes: int | None = None
    transport_minutes: int | None = None
    description: str | None = None
    address: str | None = None
    lat: float | None = None
    lng: float | None = None
    photos: list[str]
    amenities: list[str]
    status: DirectoryStatus


# ─── Airline ───
class AirlineIn(BaseModel):
    name: str
    iata: str = Field(min_length=2, max_length=3)
    country: str | None = None
    base_iata: str | None = None
    base_city: str | None = None
    logo_url: str | None = None
    logo_color: str | None = None
    status: DirectoryStatus = DirectoryStatus.ACTIVE


class AirlineOut(TimestampedSchema):
    name: str
    iata: str
    country: str | None = None
    base_iata: str | None = None
    base_city: str | None = None
    logo_url: str | None = None
    logo_color: str | None = None
    status: DirectoryStatus


# ─── Service ───
class ServiceIn(BaseModel):
    icon: str | None = None
    name: str
    description: str | None = None
    category: ServiceCategory = ServiceCategory.OTHER
    status: DirectoryStatus = DirectoryStatus.ACTIVE


class ServiceOut(TimestampedSchema):
    icon: str | None = None
    name: str
    description: str | None = None
    category: ServiceCategory
    status: DirectoryStatus


# ─── Gift ───
class GiftIn(BaseModel):
    icon: str | None = None
    name: str
    description: str | None = None
    cost_uzs: int | None = None
    brand: GiftBrand = GiftBrand.STANDARD
    status: DirectoryStatus = DirectoryStatus.ACTIVE


class GiftOut(TimestampedSchema):
    icon: str | None = None
    name: str
    description: str | None = None
    cost_uzs: int | None = None
    brand: GiftBrand
    status: DirectoryStatus


# ─── MealType / PackageType / TransferType / RejectReason — простые ───
class SimpleDictIn(BaseModel):
    name: str
    description: str | None = None
    icon: str | None = None
    status: DirectoryStatus = DirectoryStatus.ACTIVE


class SimpleDictOut(TimestampedSchema):
    name: str
    description: str | None = None
    icon: str | None = None
    status: DirectoryStatus


# ─── InventoryType ───
class InventoryTypeIn(BaseModel):
    code: RoomType
    label: str
    capacity: int = Field(ge=1, le=10)
    gender_constraint: str | None = None
    description: str | None = None
    is_globally_enabled: bool = True
    sort_order: int = 0


class InventoryTypeOut(TimestampedSchema):
    code: RoomType
    label: str
    capacity: int
    gender_constraint: str | None = None
    description: str | None = None
    is_globally_enabled: bool
    sort_order: int
