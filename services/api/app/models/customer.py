"""Клиент-паломник (пользователь Mini App / сайта) + его паломники + махрам-связи."""

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import DocumentType, Gender, Locale, MahramRelation


class Customer(Base):
    __tablename__ = "customers"

    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(200), unique=True, nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[Gender | None] = mapped_column(String(2), nullable=True)
    locale: Mapped[Locale] = mapped_column(String(10), default=Locale.UZ_CYRL, nullable=False)

    # Click ID для интеграции
    click_user_id: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)

    notifications_push: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notifications_geo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notifications_marketing: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    pilgrims: Mapped[list["Pilgrim"]] = relationship(
        back_populates="customer", cascade="all, delete-orphan"
    )


class Pilgrim(Base):
    __tablename__ = "pilgrims"

    customer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), index=True
    )
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    full_name: Mapped[str] = mapped_column(String(300), nullable=False)
    gender: Mapped[Gender] = mapped_column(String(2), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Документ
    document_type: Mapped[DocumentType] = mapped_column(
        String(20), default=DocumentType.ZAGRAN, nullable=False
    )
    document_series_number: Mapped[str | None] = mapped_column(String(40), nullable=True)
    document_valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    document_file_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Махрам — двусторонняя связь (если эта женщина имеет махрама-мужчину)
    mahram_pilgrim_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("pilgrims.id", ondelete="SET NULL"), nullable=True
    )
    mahram_relation: Mapped[MahramRelation | None] = mapped_column(String(20), nullable=True)

    customer: Mapped[Customer] = relationship(back_populates="pilgrims")
    mahram_pilgrim: Mapped["Pilgrim | None"] = relationship(
        remote_side="Pilgrim.id", foreign_keys=[mahram_pilgrim_id]
    )
