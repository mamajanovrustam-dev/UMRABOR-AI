"""Аудит-лог UMRABOR Платформы и АРМ Партнёра."""

from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import AuditAction


class AuditLog(Base):
    __tablename__ = "audit_logs"

    actor_kind: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    actor_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), index=True, nullable=True)
    actor_name: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Если действие касается партнёра, фиксируем чей это контекст
    scope_partner_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("partners.id", ondelete="SET NULL"), nullable=True
    )

    action: Mapped[AuditAction] = mapped_column(String(30), nullable=False, index=True)
    object_kind: Mapped[str] = mapped_column(String(40), nullable=False)
    object_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    object_label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}", nullable=False)


class Notification(Base):
    """Уведомления, доставленные пользователям (push/sms/email)."""

    __tablename__ = "notifications"

    recipient_kind: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    recipient_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), index=True, nullable=False)
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    trigger: Mapped[str] = mapped_column(String(40), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}", nullable=False)
    read_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
