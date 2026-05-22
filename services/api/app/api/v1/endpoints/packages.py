"""Endpoints для пакетов:
- Партнёр: CRUD своих пакетов + отправка на модерацию.
- Платформа: список всех пакетов, модерация.
- Публично (для каталога Mini App / сайта): только опубликованные пакеты.
"""

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.api.deps import (
    CurrentPartnerEmployee,
    CurrentUmrabor,
    DbSession,
)
from app.models import (
    Departure,
    DepartureInventory,
    Hotel,
    Package,
    PackageGift,
    PackageHotel,
    PackageModeration,
    PackageService,
    Partner,
)
from app.models.enums import (
    AuditAction,
    ModerationDecision,
    PackageStatus,
    PartnerRole,
)
from app.schemas.common import OkResponse, PageParams, Paginated
from app.schemas.package import (
    DepartureIn,
    DepartureInventoryOut,
    DepartureOut,
    HotelInPackageOut,
    PackageCreate,
    PackageDetailOut,
    PackageModerationIn,
    PackageOut,
    PackageUpdate,
)
from app.services.audit import audit

router = APIRouter()


async def _build_package_out(db: AsyncSession, p: Package, include_departures: bool = False) -> dict:
    # Загружаем партнёра отдельно
    partner = await db.get(Partner, p.partner_id)

    # Hotels
    hotel_rows = (await db.execute(
        select(PackageHotel, Hotel)
        .join(Hotel, PackageHotel.hotel_id == Hotel.id)
        .where(PackageHotel.package_id == p.id)
        .order_by(PackageHotel.sort_order)
    )).all()
    hotels = [
        HotelInPackageOut(
            id=ph.id, hotel_id=h.id, hotel_name=h.name,
            hotel_city=h.city, hotel_stars=h.stars,
            nights=ph.nights, sort_order=ph.sort_order,
        )
        for ph, h in hotel_rows
    ]

    # Services & gifts
    svc_ids = (await db.execute(
        select(PackageService.service_id).where(PackageService.package_id == p.id)
    )).scalars().all()
    gift_ids = (await db.execute(
        select(PackageGift.gift_id).where(PackageGift.package_id == p.id)
    )).scalars().all()

    # Departures count + sold
    dep_stats = (await db.execute(
        select(func.count(Departure.id), func.coalesce(func.sum(Departure.sold_total), 0))
        .where(Departure.package_id == p.id)
    )).one()

    base = {
        "id": p.id,
        "created_at": p.created_at,
        "updated_at": p.updated_at,
        "partner_id": p.partner_id,
        "partner_brand": partner.brand if partner else None,
        "name": p.name,
        "slug": p.slug,
        "package_type_id": p.package_type_id,
        "airline_id": p.airline_id,
        "transfer_type_id": p.transfer_type_id,
        "meal_type_id": p.meal_type_id,
        "route": p.route,
        "duration_days": p.duration_days,
        "description": p.description,
        "photos": p.photos,
        "price_sgl": p.price_sgl,
        "price_dbl": p.price_dbl,
        "price_trpl": p.price_trpl,
        "price_quad": p.price_quad,
        "status": p.status,
        "submitted_at": p.submitted_at,
        "moderated_at": p.moderated_at,
        "moderation_note": p.moderation_note,
        "hotels": hotels,
        "service_ids": list(svc_ids),
        "gift_ids": list(gift_ids),
        "departures_count": dep_stats[0] or 0,
        "sold_total": dep_stats[1] or 0,
    }

    if include_departures:
        deps = (await db.execute(
            select(Departure)
            .where(Departure.package_id == p.id)
            .order_by(Departure.date_out)
            .options(selectinload(Departure.inventory_slots))
        )).scalars().all()
        base["departures"] = [
            DepartureOut(
                id=d.id, created_at=d.created_at, updated_at=d.updated_at,
                package_id=d.package_id, date_out=d.date_out, date_in=d.date_in,
                flight_out=d.flight_out, flight_in=d.flight_in,
                aircraft=d.aircraft, baggage=d.baggage,
                capacity_total=d.capacity_total, sold_total=d.sold_total,
                price_sgl=d.price_sgl, price_dbl=d.price_dbl,
                price_trpl=d.price_trpl, price_quad=d.price_quad,
                is_active=d.is_active,
                inventory=[DepartureInventoryOut.model_validate(s) for s in d.inventory_slots],
            ).model_dump()
            for d in deps
        ]

    return base


# ════════════ Public каталог (для Mini App / сайта) ════════════
@router.get("/public", response_model=Paginated[PackageOut])
async def list_public_packages(
    db: DbSession, page: int = 1, page_size: int = 20
) -> Paginated[PackageOut]:
    pp = PageParams(page=page, page_size=page_size)
    base_stmt = select(Package).where(Package.status == PackageStatus.PUBLISHED)
    total = (await db.execute(
        select(func.count(Package.id)).where(Package.status == PackageStatus.PUBLISHED)
    )).scalar_one()
    res = await db.execute(base_stmt.order_by(Package.name).offset(pp.offset).limit(pp.page_size))
    items = []
    for p in res.scalars().all():
        items.append(PackageOut.model_validate(await _build_package_out(db, p)))
    return Paginated(items=items, total=total, page=pp.page, page_size=pp.page_size)


@router.get("/public/{slug}", response_model=PackageDetailOut)
async def get_public_package(slug: str, db: DbSession) -> PackageDetailOut:
    res = await db.execute(
        select(Package).where(
            Package.slug == slug, Package.status == PackageStatus.PUBLISHED
        )
    )
    p = res.scalar_one_or_none()
    if p is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Пакет не найден")
    return PackageDetailOut.model_validate(await _build_package_out(db, p, include_departures=True))


# ════════════ Партнёр: свои пакеты ════════════
@router.get("/me", response_model=Paginated[PackageOut])
async def list_my_packages(
    emp: CurrentPartnerEmployee,
    db: DbSession,
    page: int = 1,
    page_size: int = 50,
    status_filter: PackageStatus | None = None,
) -> Paginated[PackageOut]:
    pp = PageParams(page=page, page_size=page_size)
    base = select(Package).where(Package.partner_id == emp.partner_id)
    count_stmt = select(func.count(Package.id)).where(Package.partner_id == emp.partner_id)
    if status_filter:
        base = base.where(Package.status == status_filter)
        count_stmt = count_stmt.where(Package.status == status_filter)
    total = (await db.execute(count_stmt)).scalar_one()
    res = await db.execute(base.order_by(Package.created_at.desc()).offset(pp.offset).limit(pp.page_size))
    items = []
    for p in res.scalars().all():
        items.append(PackageOut.model_validate(await _build_package_out(db, p)))
    return Paginated(items=items, total=total, page=pp.page, page_size=pp.page_size)


@router.get("/me/{package_id}", response_model=PackageDetailOut)
async def get_my_package(
    package_id: UUID, emp: CurrentPartnerEmployee, db: DbSession
) -> PackageDetailOut:
    p = await db.get(Package, package_id)
    if p is None or p.partner_id != emp.partner_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Пакет не найден")
    return PackageDetailOut.model_validate(await _build_package_out(db, p, include_departures=True))


@router.post(
    "/me", response_model=PackageOut, status_code=status.HTTP_201_CREATED
)
async def create_package(
    payload: PackageCreate, emp: CurrentPartnerEmployee, db: DbSession
) -> PackageOut:
    if emp.role != PartnerRole.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Только админ партнёра может создавать пакеты")

    data = payload.model_dump()
    hotels = data.pop("hotels", [])
    service_ids = data.pop("service_ids", [])
    gift_ids = data.pop("gift_ids", [])

    p = Package(partner_id=emp.partner_id, status=PackageStatus.DRAFT, **data)
    db.add(p)
    try:
        await db.flush()
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Slug пакета уже занят") from e

    for h in hotels:
        db.add(PackageHotel(
            package_id=p.id,
            hotel_id=h["hotel_id"],
            nights=h["nights"],
            sort_order=h.get("sort_order", 0),
        ))
    for sid in service_ids:
        db.add(PackageService(package_id=p.id, service_id=sid))
    for gid in gift_ids:
        db.add(PackageGift(package_id=p.id, gift_id=gid))

    await audit(
        db, actor_kind="partner", actor_id=emp.id, actor_name=emp.full_name,
        action=AuditAction.CREATE, object_kind="package",
        object_id=p.id, object_label=p.name, scope_partner_id=p.partner_id,
    )
    await db.commit()
    await db.refresh(p)
    return PackageOut.model_validate(await _build_package_out(db, p))


@router.put("/me/{package_id}", response_model=PackageOut)
async def update_package(
    package_id: UUID,
    payload: PackageUpdate,
    emp: CurrentPartnerEmployee,
    db: DbSession,
) -> PackageOut:
    if emp.role != PartnerRole.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Только админ партнёра")
    p = await db.get(Package, package_id)
    if p is None or p.partner_id != emp.partner_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Пакет не найден")

    data = payload.model_dump()
    hotels = data.pop("hotels", [])
    service_ids = data.pop("service_ids", [])
    gift_ids = data.pop("gift_ids", [])
    for k, v in data.items():
        setattr(p, k, v)

    # Простой подход: пересоздаём связки
    await db.execute(PackageHotel.__table__.delete().where(PackageHotel.package_id == p.id))
    await db.execute(PackageService.__table__.delete().where(PackageService.package_id == p.id))
    await db.execute(PackageGift.__table__.delete().where(PackageGift.package_id == p.id))
    for h in hotels:
        db.add(PackageHotel(
            package_id=p.id, hotel_id=h["hotel_id"], nights=h["nights"],
            sort_order=h.get("sort_order", 0),
        ))
    for sid in service_ids:
        db.add(PackageService(package_id=p.id, service_id=sid))
    for gid in gift_ids:
        db.add(PackageGift(package_id=p.id, gift_id=gid))

    # Если пакет был опубликован → переводим в moderation после правок
    if p.status == PackageStatus.PUBLISHED:
        p.status = PackageStatus.MODERATION
        p.submitted_at = datetime.now(UTC)

    await audit(
        db, actor_kind="partner", actor_id=emp.id, actor_name=emp.full_name,
        action=AuditAction.UPDATE, object_kind="package",
        object_id=p.id, object_label=p.name, scope_partner_id=p.partner_id,
    )
    await db.commit()
    await db.refresh(p)
    return PackageOut.model_validate(await _build_package_out(db, p))


@router.post("/me/{package_id}/submit", response_model=PackageOut)
async def submit_for_moderation(
    package_id: UUID, emp: CurrentPartnerEmployee, db: DbSession
) -> PackageOut:
    if emp.role != PartnerRole.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Только админ партнёра")
    p = await db.get(Package, package_id)
    if p is None or p.partner_id != emp.partner_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Пакет не найден")
    if p.status not in (PackageStatus.DRAFT, PackageStatus.REWORK, PackageStatus.REJECTED):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Пакет в статусе {p.status} нельзя отправить")

    p.status = PackageStatus.MODERATION
    p.submitted_at = datetime.now(UTC)
    await audit(
        db, actor_kind="partner", actor_id=emp.id, actor_name=emp.full_name,
        action=AuditAction.UPDATE, object_kind="package",
        object_id=p.id, object_label=f"{p.name} → на модерацию",
        scope_partner_id=p.partner_id,
    )
    await db.commit()
    await db.refresh(p)
    return PackageOut.model_validate(await _build_package_out(db, p))


# ════════════ Платформа: модерация ════════════
@router.get("/", response_model=Paginated[PackageOut])
async def list_all_packages(
    db: DbSession,
    _: CurrentUmrabor,
    page: int = 1,
    page_size: int = 50,
    status_filter: PackageStatus | None = None,
) -> Paginated[PackageOut]:
    pp = PageParams(page=page, page_size=page_size)
    base = select(Package)
    count_stmt = select(func.count(Package.id))
    if status_filter:
        base = base.where(Package.status == status_filter)
        count_stmt = count_stmt.where(Package.status == status_filter)
    total = (await db.execute(count_stmt)).scalar_one()
    res = await db.execute(base.order_by(Package.submitted_at.desc().nullslast()).offset(pp.offset).limit(pp.page_size))
    items = []
    for p in res.scalars().all():
        items.append(PackageOut.model_validate(await _build_package_out(db, p)))
    return Paginated(items=items, total=total, page=pp.page, page_size=pp.page_size)


@router.get("/{package_id}", response_model=PackageDetailOut)
async def get_package(
    package_id: UUID, db: DbSession, _: CurrentUmrabor
) -> PackageDetailOut:
    p = await db.get(Package, package_id)
    if p is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Пакет не найден")
    return PackageDetailOut.model_validate(await _build_package_out(db, p, include_departures=True))


@router.post("/{package_id}/moderate", response_model=PackageOut)
async def moderate_package(
    package_id: UUID,
    payload: PackageModerationIn,
    db: DbSession,
    user: CurrentUmrabor,
) -> PackageOut:
    p = await db.get(Package, package_id)
    if p is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Пакет не найден")
    if p.status != PackageStatus.MODERATION:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Пакет не на модерации")

    db.add(PackageModeration(
        package_id=p.id,
        moderator_id=user.id,
        decision=payload.decision,
        comment=payload.comment,
    ))

    action: AuditAction
    if payload.decision == ModerationDecision.APPROVED:
        p.status = PackageStatus.PUBLISHED
        action = AuditAction.PUBLISH
    elif payload.decision == ModerationDecision.REJECTED:
        p.status = PackageStatus.REJECTED
        action = AuditAction.REJECT
    else:
        p.status = PackageStatus.REWORK
        action = AuditAction.REWORK

    p.moderated_at = datetime.now(UTC)
    p.moderation_note = payload.comment

    await audit(
        db, actor_kind="umrabor", actor_id=user.id, actor_name=user.full_name,
        action=action, object_kind="package",
        object_id=p.id, object_label=p.name, scope_partner_id=p.partner_id,
        description=payload.comment,
    )
    await db.commit()
    await db.refresh(p)
    return PackageOut.model_validate(await _build_package_out(db, p))


# ════════════ Departures (партнёр) ════════════
@router.post(
    "/me/{package_id}/departures",
    response_model=DepartureOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_departure(
    package_id: UUID,
    payload: DepartureIn,
    emp: CurrentPartnerEmployee,
    db: DbSession,
) -> DepartureOut:
    if emp.role != PartnerRole.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Только админ партнёра")
    p = await db.get(Package, package_id)
    if p is None or p.partner_id != emp.partner_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Пакет не найден")

    data = payload.model_dump()
    inventory = data.pop("inventory", [])
    capacity_total = sum(item["capacity"] for item in inventory)
    d = Departure(package_id=p.id, capacity_total=capacity_total, **data)
    db.add(d)
    await db.flush()
    for item in inventory:
        db.add(DepartureInventory(
            departure_id=d.id,
            room_type=item["room_type"],
            capacity=item["capacity"],
            is_enabled=item.get("is_enabled", True),
        ))
    await db.commit()
    await db.refresh(d, ["inventory_slots"])
    return DepartureOut(
        id=d.id, created_at=d.created_at, updated_at=d.updated_at,
        package_id=d.package_id, date_out=d.date_out, date_in=d.date_in,
        flight_out=d.flight_out, flight_in=d.flight_in,
        aircraft=d.aircraft, baggage=d.baggage,
        capacity_total=d.capacity_total, sold_total=d.sold_total,
        price_sgl=d.price_sgl, price_dbl=d.price_dbl,
        price_trpl=d.price_trpl, price_quad=d.price_quad,
        is_active=d.is_active,
        inventory=[DepartureInventoryOut.model_validate(s) for s in d.inventory_slots],
    )


@router.delete("/me/departures/{departure_id}", response_model=OkResponse)
async def delete_departure(
    departure_id: UUID, emp: CurrentPartnerEmployee, db: DbSession
) -> OkResponse:
    if emp.role != PartnerRole.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Только админ партнёра")
    d = await db.get(Departure, departure_id)
    if d is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Вылет не найден")
    p = await db.get(Package, d.package_id)
    if p is None or p.partner_id != emp.partner_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Вылет не найден")
    await db.delete(d)
    await db.commit()
    return OkResponse(message="Вылет удалён")


from sqlalchemy.ext.asyncio import AsyncSession  # noqa: E402 (для type-аннотации _build_package_out)
