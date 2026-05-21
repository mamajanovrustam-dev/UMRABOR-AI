"""Аудит-лог: read-only, доступен UMRABOR (для Платформы) и партнёру-админу (только свой scope)."""

from uuid import UUID

from fastapi import APIRouter
from sqlalchemy import func, select

from app.api.deps import CurrentPartnerAdmin, CurrentUmrabor, DbSession
from app.models import AuditLog
from app.schemas.common import BaseSchema, PageParams, Paginated
from datetime import datetime


class AuditLogOut(BaseSchema):
    id: UUID
    actor_kind: str
    actor_id: UUID | None = None
    actor_name: str | None = None
    scope_partner_id: UUID | None = None
    action: str
    object_kind: str
    object_id: UUID | None = None
    object_label: str | None = None
    description: str | None = None
    ip: str | None = None
    meta: dict
    created_at: datetime


router = APIRouter()


@router.get("/", response_model=Paginated[AuditLogOut])
async def list_audit_global(
    db: DbSession,
    _: CurrentUmrabor,
    page: int = 1,
    page_size: int = 50,
) -> Paginated[AuditLogOut]:
    pp = PageParams(page=page, page_size=page_size)
    total = (await db.execute(select(func.count(AuditLog.id)))).scalar_one()
    res = await db.execute(
        select(AuditLog).order_by(AuditLog.created_at.desc()).offset(pp.offset).limit(pp.page_size)
    )
    return Paginated(
        items=[AuditLogOut.model_validate(r) for r in res.scalars().all()],
        total=total, page=pp.page, page_size=pp.page_size,
    )


@router.get("/partner", response_model=Paginated[AuditLogOut])
async def list_audit_for_partner(
    emp: CurrentPartnerAdmin,
    db: DbSession,
    page: int = 1,
    page_size: int = 50,
) -> Paginated[AuditLogOut]:
    pp = PageParams(page=page, page_size=page_size)
    base = select(AuditLog).where(AuditLog.scope_partner_id == emp.partner_id)
    cs = select(func.count(AuditLog.id)).where(AuditLog.scope_partner_id == emp.partner_id)
    total = (await db.execute(cs)).scalar_one()
    res = await db.execute(base.order_by(AuditLog.created_at.desc()).offset(pp.offset).limit(pp.page_size))
    return Paginated(
        items=[AuditLogOut.model_validate(r) for r in res.scalars().all()],
        total=total, page=pp.page, page_size=pp.page_size,
    )
