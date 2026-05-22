"""Запись действий в аудит-лог. Используется на всех изменяющих endpoint'ах."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditLog
from app.models.enums import AuditAction


async def audit(
    db: AsyncSession,
    *,
    actor_kind: str,
    action: AuditAction,
    object_kind: str,
    actor_id: UUID | None = None,
    actor_name: str | None = None,
    object_id: UUID | None = None,
    object_label: str | None = None,
    description: str | None = None,
    scope_partner_id: UUID | None = None,
    ip: str | None = None,
    user_agent: str | None = None,
    meta: dict | None = None,
) -> AuditLog:
    row = AuditLog(
        actor_kind=actor_kind,
        actor_id=actor_id,
        actor_name=actor_name,
        action=action,
        object_kind=object_kind,
        object_id=object_id,
        object_label=object_label,
        description=description,
        scope_partner_id=scope_partner_id,
        ip=ip,
        user_agent=user_agent,
        meta=meta or {},
    )
    db.add(row)
    await db.flush()
    return row
