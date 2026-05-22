"""Партнёр (тур-оператор), его сотрудники и история статусов."""

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import PartnerRole, PartnerStatus


class Partner(Base):
    __tablename__ = "partners"

    # Идентификация
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    brand: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    founded_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Лицензия
    license_no: Mapped[str | None] = mapped_column(String(50), nullable=True)
    license_authority: Mapped[str] = mapped_column(
        String(200), default="Госкомтуризм РУз", nullable=False
    )
    license_issued_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    license_until: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    license_file_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Банковские реквизиты
    inn: Mapped[str | None] = mapped_column(String(20), index=True, nullable=True)
    oked: Mapped[str | None] = mapped_column(String(20), nullable=True)
    bank_account: Mapped[str | None] = mapped_column(String(40), nullable=True)
    bank_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    bank_mfo: Mapped[str | None] = mapped_column(String(10), nullable=True)
    vat_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    legal_address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    actual_address: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Контакт-директор
    contact_full_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    contact_position: Mapped[str | None] = mapped_column(String(120), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Статус
    status: Mapped[PartnerStatus] = mapped_column(
        String(20), default=PartnerStatus.ACTIVE, nullable=False, index=True
    )
    status_changed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Внутренняя заметка UMRABOR
    internal_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ─── relations ───
    employees: Mapped[list["PartnerEmployee"]] = relationship(
        back_populates="partner", cascade="all, delete-orphan"
    )
    status_history: Mapped[list["PartnerStatusHistory"]] = relationship(
        back_populates="partner",
        cascade="all, delete-orphan",
        order_by="desc(PartnerStatusHistory.created_at)",
    )


class PartnerStatusHistory(Base):
    __tablename__ = "partner_status_history"

    partner_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("partners.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[PartnerStatus] = mapped_column(String(20), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_by_user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users_umrabor.id", ondelete="SET NULL"), nullable=True
    )

    partner: Mapped[Partner] = relationship(back_populates="status_history")


class PartnerEmployee(Base):
    __tablename__ = "partner_employees"

    partner_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("partners.id", ondelete="CASCADE"), index=True
    )
    login: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    role: Mapped[PartnerRole] = mapped_column(String(20), nullable=False, default=PartnerRole.OPERATOR)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)

    partner: Mapped[Partner] = relationship(back_populates="employees")
