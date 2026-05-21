"""Заявка → паломники → размещения. Плюс чат и сообщения."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import BookingSource, BookingStatus, ChatThreadType, RoomType


class Booking(Base):
    __tablename__ = "bookings"

    # Человекочитаемый ID (UM-2026-0061), генерируется при создании
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)

    partner_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("partners.id", ondelete="RESTRICT"), index=True
    )
    customer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("customers.id", ondelete="RESTRICT"), index=True
    )
    package_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("packages.id", ondelete="RESTRICT"), index=True
    )
    departure_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("departures.id", ondelete="RESTRICT"), index=True
    )

    source: Mapped[BookingSource] = mapped_column(
        String(20), default=BookingSource.WEB, nullable=False
    )
    click_id: Mapped[str | None] = mapped_column(String(32), nullable=True)

    status: Mapped[BookingStatus] = mapped_column(
        String(20), default=BookingStatus.NEW, nullable=False, index=True
    )
    sla_deadline_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    total_uzs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cashback_uzs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancellation_reason_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("dir_reject_reasons.id", ondelete="SET NULL"),
        nullable=True,
    )
    cancellation_comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    assigned_operator_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("partner_employees.id", ondelete="SET NULL"),
        nullable=True,
    )

    voucher_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}", nullable=False)

    pilgrims_link: Mapped[list["BookingPilgrim"]] = relationship(
        back_populates="booking", cascade="all, delete-orphan"
    )
    placements: Mapped[list["Placement"]] = relationship(
        back_populates="booking", cascade="all, delete-orphan"
    )
    events: Mapped[list["BookingEvent"]] = relationship(
        back_populates="booking",
        cascade="all, delete-orphan",
        order_by="BookingEvent.created_at",
    )


class BookingPilgrim(Base):
    """Линк паломников к заявке (паломник может ехать в нескольких заявках)."""

    __tablename__ = "booking_pilgrims"
    __table_args__ = (UniqueConstraint("booking_id", "pilgrim_id"),)

    booking_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), index=True
    )
    pilgrim_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("pilgrims.id", ondelete="RESTRICT"), index=True
    )
    placement_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("placements.id", ondelete="SET NULL"), nullable=True
    )

    booking: Mapped[Booking] = relationship(back_populates="pilgrims_link")


class Placement(Base):
    """Комната в заявке: тип + список занявших паломников + сумма."""

    __tablename__ = "placements"

    booking_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), index=True
    )
    room_type: Mapped[RoomType] = mapped_column(String(20), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_per_person_uzs: Mapped[int] = mapped_column(Integer, nullable=False)
    total_uzs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Если 1/2 ждёт подсёлку — флаг
    awaiting_co_lodger: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    booking: Mapped[Booking] = relationship(back_populates="placements")


class BookingEvent(Base):
    """Аудит-лента событий по заявке."""

    __tablename__ = "booking_events"

    booking_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), index=True
    )
    event_type: Mapped[str] = mapped_column(String(40), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    actor_kind: Mapped[str | None] = mapped_column(String(20), nullable=True)
    actor_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    actor_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}", nullable=False)

    booking: Mapped[Booking] = relationship(back_populates="events")


class ChatThread(Base):
    """Чат-тред между клиентом и партнёром (или клиент↔саппорт)."""

    __tablename__ = "chat_threads"

    thread_type: Mapped[ChatThreadType] = mapped_column(String(30), nullable=False, index=True)
    customer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), index=True
    )
    partner_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("partners.id", ondelete="CASCADE"), nullable=True
    )
    booking_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="SET NULL"), nullable=True
    )
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    customer_unread: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    partner_unread: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="thread",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    thread_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("chat_threads.id", ondelete="CASCADE"), index=True
    )
    sender_kind: Mapped[str] = mapped_column(String(20), nullable=False)
    sender_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    sender_name: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    attachments: Mapped[list] = mapped_column(
        JSONB, default=list, server_default="[]", nullable=False
    )
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    thread: Mapped[ChatThread] = relationship(back_populates="messages")
