"""Платежи через Click (и потенциально другие каналы)."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import PaymentChannel, PaymentStatus


class Payment(Base):
    __tablename__ = "payments"

    code: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    booking_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="RESTRICT"), index=True
    )
    customer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("customers.id", ondelete="RESTRICT"), index=True
    )
    partner_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("partners.id", ondelete="RESTRICT"), index=True
    )

    channel: Mapped[PaymentChannel] = mapped_column(
        String(20), default=PaymentChannel.CLICK, nullable=False
    )
    amount_uzs: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="UZS", nullable=False)

    status: Mapped[PaymentStatus] = mapped_column(
        String(20), default=PaymentStatus.PENDING, nullable=False, index=True
    )

    # Click-specific
    click_trans_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    click_paydoc_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    click_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    refund_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    refund_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    raw: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}", nullable=False)
