"""Пакет → Гостиницы (через связку) → Вылеты → Инвентарь по слотам."""

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import (
    ARRAY,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ModerationDecision, PackageStatus, RoomType


class Package(Base):
    __tablename__ = "packages"

    partner_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("partners.id", ondelete="CASCADE"), index=True
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    package_type_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("dir_package_types.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Маршрут: Жидда → Мадина → Макка → Жидда (хранится как массив строк-городов)
    route: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list, server_default="{}", nullable=False
    )
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    photos: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list, server_default="{}", nullable=False
    )

    airline_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("dir_airlines.id", ondelete="SET NULL"), nullable=True
    )
    transfer_type_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("dir_transfer_types.id", ondelete="SET NULL"),
        nullable=True,
    )
    meal_type_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("dir_meal_types.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Тарифы за 1 человека в комнате (UZS)
    price_sgl: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_dbl: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_trpl: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_quad: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Статус модерации
    status: Mapped[PackageStatus] = mapped_column(
        String(20), default=PackageStatus.DRAFT, nullable=False, index=True
    )
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    moderated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    moderation_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    hotels: Mapped[list["PackageHotel"]] = relationship(
        back_populates="package", cascade="all, delete-orphan"
    )
    departures: Mapped[list["Departure"]] = relationship(
        back_populates="package", cascade="all, delete-orphan"
    )
    services: Mapped[list["PackageService"]] = relationship(
        back_populates="package", cascade="all, delete-orphan"
    )
    gifts: Mapped[list["PackageGift"]] = relationship(
        back_populates="package", cascade="all, delete-orphan"
    )
    moderation_events: Mapped[list["PackageModeration"]] = relationship(
        back_populates="package",
        cascade="all, delete-orphan",
        order_by="desc(PackageModeration.created_at)",
    )


class PackageHotel(Base):
    """Связка пакет-отель с кол-вом ночей и порядком в маршруте."""

    __tablename__ = "package_hotels"

    package_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("packages.id", ondelete="CASCADE"), index=True
    )
    hotel_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("dir_hotels.id", ondelete="RESTRICT"), index=True
    )
    nights: Mapped[int] = mapped_column(Integer, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    package: Mapped[Package] = relationship(back_populates="hotels")


class PackageService(Base):
    __tablename__ = "package_services"
    __table_args__ = (UniqueConstraint("package_id", "service_id"),)

    package_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("packages.id", ondelete="CASCADE"), index=True
    )
    service_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("dir_services.id", ondelete="RESTRICT"), index=True
    )
    package: Mapped[Package] = relationship(back_populates="services")


class PackageGift(Base):
    __tablename__ = "package_gifts"
    __table_args__ = (UniqueConstraint("package_id", "gift_id"),)

    package_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("packages.id", ondelete="CASCADE"), index=True
    )
    gift_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("dir_gifts.id", ondelete="RESTRICT"), index=True
    )
    package: Mapped[Package] = relationship(back_populates="gifts")


class Departure(Base):
    """Конкретный вылет пакета — дата туда + дата обратно + рейсы + инвентарь по типам комнат."""

    __tablename__ = "departures"

    package_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("packages.id", ondelete="CASCADE"), index=True
    )
    date_out: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    date_in: Mapped[date] = mapped_column(Date, nullable=False)
    flight_out: Mapped[str | None] = mapped_column(String(20), nullable=True)
    flight_in: Mapped[str | None] = mapped_column(String(20), nullable=True)
    aircraft: Mapped[str | None] = mapped_column(String(120), nullable=True)
    baggage: Mapped[str | None] = mapped_column(String(50), nullable=True)
    capacity_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sold_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Override-тарифы (если отличаются от пакета)
    price_sgl: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_dbl: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_trpl: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_quad: Mapped[int | None] = mapped_column(Integer, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    package: Mapped[Package] = relationship(back_populates="departures")
    inventory_slots: Mapped[list["DepartureInventory"]] = relationship(
        back_populates="departure", cascade="all, delete-orphan"
    )


class DepartureInventory(Base):
    """Инвентарь по типу комнаты для конкретного вылета."""

    __tablename__ = "departure_inventory"
    __table_args__ = (UniqueConstraint("departure_id", "room_type"),)

    departure_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("departures.id", ondelete="CASCADE"), index=True
    )
    room_type: Mapped[RoomType] = mapped_column(String(20), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sold: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    departure: Mapped[Departure] = relationship(back_populates="inventory_slots")


class PackageModeration(Base):
    """Лог модерации пакета: одобрено / отклонено / на доработку + комментарии."""

    __tablename__ = "package_moderation_events"

    package_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("packages.id", ondelete="CASCADE"), index=True
    )
    moderator_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users_umrabor.id", ondelete="SET NULL"), nullable=True
    )
    decision: Mapped[ModerationDecision] = mapped_column(String(20), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    diff: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}", nullable=False)

    package: Mapped[Package] = relationship(back_populates="moderation_events")


# Денежные значения хранятся как Integer (UZS — целое число копеек/сум).
_ = Numeric  # noqa: F841 — оставляем импорт для совместимости с будущими decimal-полями
