"""Endpoints для управления партнёрами (только UMRABOR). Партнёр свой профиль — read-only."""

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.api.deps import (
    CurrentPartnerEmployee,
    CurrentUmrabor,
    CurrentUmraborSuper,
    DbSession,
)
from app.core.security import hash_password
from app.models import (
    Partner,
    PartnerEmployee,
    PartnerStatusHistory,
)
from app.models.enums import AuditAction, PartnerRole, PartnerStatus
from app.schemas.common import OkResponse, PageParams, Paginated
from app.schemas.partner import (
    PartnerCreate,
    PartnerEmployeeCreate,
    PartnerEmployeeOut,
    PartnerEmployeeUpdate,
    PartnerOut,
    PartnerStatusChangeIn,
    PartnerStatusHistoryItem,
    PartnerUpdate,
)
from app.services.audit import audit

router = APIRouter()


# ════════════ Платформа: список и регистрация ════════════
@router.get("/", response_model=Paginated[PartnerOut])
async def list_partners(
    db: DbSession,
    _: CurrentUmrabor,
    page: int = 1,
    page_size: int = 50,
    status_filter: PartnerStatus | None = None,
    q: str | None = None,
) -> Paginated[PartnerOut]:
    pp = PageParams(page=page, page_size=page_size)
    stmt = select(Partner)
    count_stmt = select(func.count(Partner.id))
    if status_filter:
        stmt = stmt.where(Partner.status == status_filter)
        count_stmt = count_stmt.where(Partner.status == status_filter)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(Partner.brand.ilike(like))
        count_stmt = count_stmt.where(Partner.brand.ilike(like))

    total = (await db.execute(count_stmt)).scalar_one()
    res = await db.execute(stmt.order_by(Partner.brand).offset(pp.offset).limit(pp.page_size))
    return Paginated(
        items=[PartnerOut.model_validate(r) for r in res.scalars().all()],
        total=total,
        page=pp.page,
        page_size=pp.page_size,
    )


@router.post("/", response_model=PartnerOut, status_code=status.HTTP_201_CREATED)
async def create_partner(
    payload: PartnerCreate,
    db: DbSession,
    user: CurrentUmraborSuper,
) -> PartnerOut:
    data = payload.model_dump()
    admin_first = data.pop("admin_first_name")
    admin_last = data.pop("admin_last_name")
    admin_login = data.pop("admin_login")
    admin_password = data.pop("admin_password")
    admin_phone = data.pop("admin_phone", None)
    admin_email = data.pop("admin_email", None)

    partner = Partner(status=PartnerStatus.ACTIVE, **data)
    db.add(partner)
    try:
        await db.flush()
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Партнёр со slug уже существует") from e

    admin = PartnerEmployee(
        partner_id=partner.id,
        login=admin_login,
        first_name=admin_first,
        last_name=admin_last,
        full_name=f"{admin_first} {admin_last}",
        password_hash=hash_password(admin_password),
        must_change_password=True,
        role=PartnerRole.ADMIN,
        phone=admin_phone,
        email=admin_email,
    )
    db.add(admin)

    history = PartnerStatusHistory(
        partner_id=partner.id,
        status=PartnerStatus.ACTIVE,
        reason="Регистрация партнёра",
        changed_by_user_id=user.id,
    )
    db.add(history)

    await audit(
        db,
        actor_kind="umrabor",
        actor_id=user.id,
        actor_name=user.full_name,
        action=AuditAction.CREATE,
        object_kind="partner",
        object_id=partner.id,
        object_label=partner.brand,
        scope_partner_id=partner.id,
    )

    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Логин администратора уже занят") from e

    await db.refresh(partner)
    return PartnerOut.model_validate(partner)


@router.get("/{partner_id}", response_model=PartnerOut)
async def get_partner_by_id(
    partner_id: UUID, db: DbSession, _: CurrentUmrabor
) -> PartnerOut:
    p = await db.get(Partner, partner_id)
    if p is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Партнёр не найден")
    return PartnerOut.model_validate(p)


@router.put("/{partner_id}", response_model=PartnerOut)
async def update_partner(
    partner_id: UUID,
    payload: PartnerUpdate,
    db: DbSession,
    user: CurrentUmraborSuper,
) -> PartnerOut:
    p = await db.get(Partner, partner_id)
    if p is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Партнёр не найден")
    for k, v in payload.model_dump().items():
        setattr(p, k, v)
    await audit(
        db, actor_kind="umrabor", actor_id=user.id, actor_name=user.full_name,
        action=AuditAction.UPDATE, object_kind="partner",
        object_id=p.id, object_label=p.brand, scope_partner_id=p.id,
    )
    await db.commit()
    await db.refresh(p)
    return PartnerOut.model_validate(p)


@router.post("/{partner_id}/status", response_model=PartnerOut)
async def change_partner_status(
    partner_id: UUID,
    payload: PartnerStatusChangeIn,
    db: DbSession,
    user: CurrentUmraborSuper,
) -> PartnerOut:
    p = await db.get(Partner, partner_id)
    if p is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Партнёр не найден")
    if payload.status == PartnerStatus.SUSPENDED and not payload.reason:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нужна причина приостановки")

    p.status = payload.status
    p.status_changed_at = datetime.now(UTC)

    db.add(PartnerStatusHistory(
        partner_id=p.id,
        status=payload.status,
        reason=payload.reason,
        changed_by_user_id=user.id,
    ))

    audit_action = {
        PartnerStatus.SUSPENDED: AuditAction.SUSPEND,
        PartnerStatus.ACTIVE: AuditAction.REACTIVATE,
        PartnerStatus.ARCHIVED: AuditAction.UPDATE,
    }.get(payload.status, AuditAction.UPDATE)

    await audit(
        db, actor_kind="umrabor", actor_id=user.id, actor_name=user.full_name,
        action=audit_action, object_kind="partner",
        object_id=p.id, object_label=p.brand, scope_partner_id=p.id,
        description=payload.reason,
    )
    await db.commit()
    await db.refresh(p)
    return PartnerOut.model_validate(p)


@router.get(
    "/{partner_id}/status-history", response_model=list[PartnerStatusHistoryItem]
)
async def list_partner_status_history(
    partner_id: UUID, db: DbSession, _: CurrentUmrabor
) -> list[PartnerStatusHistoryItem]:
    res = await db.execute(
        select(PartnerStatusHistory)
        .where(PartnerStatusHistory.partner_id == partner_id)
        .order_by(PartnerStatusHistory.created_at.desc())
    )
    return [PartnerStatusHistoryItem.model_validate(r) for r in res.scalars().all()]


# ════════════ Партнёр: свой профиль (read-only) ════════════
@router.get("/me/profile", response_model=PartnerOut)
async def get_my_partner_profile(
    emp: CurrentPartnerEmployee, db: DbSession
) -> PartnerOut:
    p = await db.get(Partner, emp.partner_id)
    if p is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Партнёр не найден")
    return PartnerOut.model_validate(p)


# ════════════ Сотрудники партнёра (управление — только админ партнёра) ════════════
@router.get("/me/employees", response_model=list[PartnerEmployeeOut])
async def list_my_employees(
    emp: CurrentPartnerEmployee, db: DbSession
) -> list[PartnerEmployeeOut]:
    res = await db.execute(
        select(PartnerEmployee)
        .where(PartnerEmployee.partner_id == emp.partner_id)
        .order_by(PartnerEmployee.role.desc(), PartnerEmployee.full_name)
    )
    return [PartnerEmployeeOut.model_validate(r) for r in res.scalars().all()]


@router.post(
    "/me/employees",
    response_model=PartnerEmployeeOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_my_employee(
    payload: PartnerEmployeeCreate, emp: CurrentPartnerEmployee, db: DbSession
) -> PartnerEmployeeOut:
    if emp.role != PartnerRole.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Требуется роль Админ партнёра")
    new = PartnerEmployee(
        partner_id=emp.partner_id,
        login=payload.login,
        first_name=payload.first_name,
        last_name=payload.last_name,
        full_name=f"{payload.first_name} {payload.last_name}",
        phone=payload.phone,
        email=payload.email,
        password_hash=hash_password(payload.password),
        must_change_password=True,
        role=payload.role,
    )
    db.add(new)
    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Логин уже занят") from e
    await db.refresh(new)
    return PartnerEmployeeOut.model_validate(new)


@router.put(
    "/me/employees/{employee_id}", response_model=PartnerEmployeeOut
)
async def update_my_employee(
    employee_id: UUID,
    payload: PartnerEmployeeUpdate,
    emp: CurrentPartnerEmployee,
    db: DbSession,
) -> PartnerEmployeeOut:
    if emp.role != PartnerRole.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Требуется роль Админ партнёра")
    target = await db.get(PartnerEmployee, employee_id)
    if target is None or target.partner_id != emp.partner_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Сотрудник не найден")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(target, k, v)
    if payload.first_name or payload.last_name:
        target.full_name = f"{target.first_name or ''} {target.last_name or ''}".strip()
    await db.commit()
    await db.refresh(target)
    return PartnerEmployeeOut.model_validate(target)


@router.delete("/me/employees/{employee_id}", response_model=OkResponse)
async def deactivate_my_employee(
    employee_id: UUID, emp: CurrentPartnerEmployee, db: DbSession
) -> OkResponse:
    if emp.role != PartnerRole.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Требуется роль Админ партнёра")
    target = await db.get(PartnerEmployee, employee_id)
    if target is None or target.partner_id != emp.partner_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Сотрудник не найден")
    target.is_active = False
    await db.commit()
    return OkResponse(message="Сотрудник отключён")


# Suppress unused-imports warning from selectinload (used by future expansions)
_ = selectinload
