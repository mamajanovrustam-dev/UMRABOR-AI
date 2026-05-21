"""8 глобальных справочников UMRABOR."""

from uuid import UUID

from sqlalchemy import ARRAY, Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import City, DirectoryStatus, GiftBrand, RoomType, ServiceCategory


class Hotel(Base):
    __tablename__ = "dir_hotels"

    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    city: Mapped[City] = mapped_column(String(20), nullable=False, index=True)
    stars: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    distance_value: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    distance_unit: Mapped[str] = mapped_column(String(2), default="м", nullable=False)
    walk_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    transport_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    lat: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    lng: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    photos: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list, server_default="{}", nullable=False
    )
    amenities: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list, server_default="{}", nullable=False
    )
    status: Mapped[DirectoryStatus] = mapped_column(
        String(20), default=DirectoryStatus.ACTIVE, nullable=False
    )


class Airline(Base):
    __tablename__ = "dir_airlines"

    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    iata: Mapped[str] = mapped_column(String(3), unique=True, nullable=False, index=True)
    country: Mapped[str | None] = mapped_column(String(80), nullable=True)
    base_iata: Mapped[str | None] = mapped_column(String(3), nullable=True)
    base_city: Mapped[str | None] = mapped_column(String(80), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    logo_color: Mapped[str | None] = mapped_column(String(8), nullable=True)
    status: Mapped[DirectoryStatus] = mapped_column(
        String(20), default=DirectoryStatus.ACTIVE, nullable=False
    )


class Service(Base):
    __tablename__ = "dir_services"

    icon: Mapped[str | None] = mapped_column(String(10), nullable=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(300), nullable=True)
    category: Mapped[ServiceCategory] = mapped_column(
        String(20), default=ServiceCategory.OTHER, nullable=False
    )
    status: Mapped[DirectoryStatus] = mapped_column(
        String(20), default=DirectoryStatus.ACTIVE, nullable=False
    )


class Gift(Base):
    __tablename__ = "dir_gifts"

    icon: Mapped[str | None] = mapped_column(String(10), nullable=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(300), nullable=True)
    cost_uzs: Mapped[int | None] = mapped_column(Integer, nullable=True)
    brand: Mapped[GiftBrand] = mapped_column(String(20), default=GiftBrand.STANDARD, nullable=False)
    status: Mapped[DirectoryStatus] = mapped_column(
        String(20), default=DirectoryStatus.ACTIVE, nullable=False
    )


class MealType(Base):
    __tablename__ = "dir_meal_types"

    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String(300), nullable=True)
    status: Mapped[DirectoryStatus] = mapped_column(
        String(20), default=DirectoryStatus.ACTIVE, nullable=False
    )


class PackageTypeDir(Base):
    __tablename__ = "dir_package_types"

    name: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String(300), nullable=True)
    status: Mapped[DirectoryStatus] = mapped_column(
        String(20), default=DirectoryStatus.ACTIVE, nullable=False
    )


class TransferType(Base):
    __tablename__ = "dir_transfer_types"

    icon: Mapped[str | None] = mapped_column(String(10), nullable=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    status: Mapped[DirectoryStatus] = mapped_column(
        String(20), default=DirectoryStatus.ACTIVE, nullable=False
    )


class RejectReason(Base):
    __tablename__ = "dir_reject_reasons"

    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[DirectoryStatus] = mapped_column(
        String(20), default=DirectoryStatus.ACTIVE, nullable=False
    )


class InventoryType(Base):
    """Типы размещения (SGL/DBL F/DBL M/DBL FM/...) — глобально включает/отключает Платформа."""

    __tablename__ = "dir_inventory_types"

    code: Mapped[RoomType] = mapped_column(String(20), unique=True, nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(120), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    gender_constraint: Mapped[str | None] = mapped_column(String(2), nullable=True)  # F/M/FM/null
    description: Mapped[str | None] = mapped_column(String(300), nullable=True)
    is_globally_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class PartnerInventorySetting(Base):
    """Партнёр может выключить тип размещения у себя (видимый только если не globally_off)."""

    __tablename__ = "partner_inventory_settings"

    partner_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("partners.id", ondelete="CASCADE"), index=True
    )
    inventory_type_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("dir_inventory_types.id", ondelete="CASCADE"),
        index=True,
    )
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}", nullable=False)

    inventory_type: Mapped[InventoryType] = relationship()
