"""Заявки: создание клиентом, обработка партнёром, чтение Платформой."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.api.deps import (
    CurrentCustomer,
    CurrentPartnerEmployee,
    CurrentUmrabor,
    DbSession,
)
from app.models import (
    Booking,
    BookingEvent,
    BookingPilgrim,
    Departure,
    DepartureInventory,
    Package,
    Partner,
    Payment,
    Pilgrim,
    Placement,
)
from app.models.enums import (
    AuditAction,
    BookingStatus,
    PartnerRole,
    PaymentChannel,
    PaymentStatus,
    RoomType,
)
from app.schemas.booking import (
    BookingCreate,
    BookingDetailOut,
    BookingEventOut,
    BookingOut,
    BookingRejectIn,
    PilgrimMini,
    PlacementOut,
)
from app.schemas.common import OkResponse, PageParams, Paginated
from app.services.audit import audit
from app.services.codes import next_booking_code, next_payment_code

router = APIRouter()


_CAPACITY_BY_ROOM_TYPE: dict[RoomType, int] = {
    RoomType.SGL: 1,
    RoomType.DBL_F: 2, RoomType.DBL_M: 2, RoomType.DBL_FM: 2,
    RoomType.TRPL_F: 3, RoomType.TRPL_M: 3, RoomType.TRPL_FM: 3,
    RoomType.QUAD_F: 4, RoomType.QUAD_M: 4, RoomType.QUAD_FM: 4,
    RoomType.QUAD_F3: 4, RoomType.QUAD_M3: 4,
}


def _price_field(rt: RoomType) -> str:
    if rt == RoomType.SGL:
        return "sgl"
    if rt in (RoomType.DBL_F, RoomType.DBL_M, RoomType.DBL_FM):
        return "dbl"
    if rt in (RoomType.TRPL_F, RoomType.TRPL_M, RoomType.TRPL_FM):
        return "trpl"
    return "quad"


async def _build_booking_out(db, b: Booking) -> dict:
    partner = await db.get(Partner, b.partner_id)
    package = await db.get(Package, b.package_id)
    departure = await db.get(Departure, b.departure_id)

    return {
        "id": b.id,
        "created_at": b.created_at,
        "updated_at": b.updated_at,
        "code": b.code,
        "partner_id": b.partner_id,
        "partner_brand": partner.brand if partner else None,
        "customer_id": b.customer_id,
        "package_id": b.package_id,
        "package_name": package.name if package else None,
        "departure_id": b.departure_id,
        "departure_date_out": departure.date_out if departure else None,
        "departure_date_in": departure.date_in if departure else None,
        "source": b.source,
        "click_id": b.click_id,
        "status": b.status,
        "sla_deadline_at": b.sla_deadline_at,
        "total_uzs": b.total_uzs,
        "cashback_uzs": b.cashback_uzs,
        "confirmed_at": b.confirmed_at,
        "completed_at": b.completed_at,
        "cancelled_at": b.cancelled_at,
        "voucher_url": b.voucher_url,
    }


async def _build_booking_detail(db, b: Booking) -> dict:
    base = await _build_booking_out(db, b)

    # Customer
    from app.models import Customer
    customer = await db.get(Customer, b.customer_id)
    base["customer_name"] = customer.full_name if customer else None
    base["customer_phone"] = customer.phone if customer else None

    # Pilgrims
    res = await db.execute(
        select(BookingPilgrim, Pilgrim)
        .join(Pilgrim, BookingPilgrim.pilgrim_id == Pilgrim.id)
        .where(BookingPilgrim.booking_id == b.id)
    )
    pilgrims: list[PilgrimMini] = []
    placement_pilgrims_map: dict[UUID, list[UUID]] = {}
    for bp, p in res.all():
        mahram_name = None
        if p.mahram_pilgrim_id:
            mp = await db.get(Pilgrim, p.mahram_pilgrim_id)
            mahram_name = mp.full_name if mp else None
        pilgrims.append(PilgrimMini(
            id=p.id, full_name=p.full_name, gender=p.gender,
            document_type=p.document_type,
            document_series_number=p.document_series_number,
            has_mahram=p.mahram_pilgrim_id is not None,
            mahram_id=p.mahram_pilgrim_id,
            mahram_name=mahram_name,
            mahram_relation=p.mahram_relation,
        ))
        if bp.placement_id:
            placement_pilgrims_map.setdefault(bp.placement_id, []).append(p.id)
    base["pilgrims"] = pilgrims

    # Placements
    placements_res = await db.execute(
        select(Placement).where(Placement.booking_id == b.id).order_by(Placement.created_at)
    )
    placements = []
    for pl in placements_res.scalars().all():
        placements.append(PlacementOut(
            id=pl.id, room_type=pl.room_type, capacity=pl.capacity,
            price_per_person_uzs=pl.price_per_person_uzs, total_uzs=pl.total_uzs,
            awaiting_co_lodger=pl.awaiting_co_lodger,
            pilgrim_ids=placement_pilgrims_map.get(pl.id, []),
        ))
    base["placements"] = placements

    # Events
    events_res = await db.execute(
        select(BookingEvent).where(BookingEvent.booking_id == b.id).order_by(BookingEvent.created_at)
    )
    base["events"] = [BookingEventOut.model_validate(e) for e in events_res.scalars().all()]

    return base


# ════════════ Клиент: создание заявки ════════════
@router.post(
    "/", response_model=BookingDetailOut, status_code=status.HTTP_201_CREATED
)
async def create_booking(
    payload: BookingCreate, customer: CurrentCustomer, db: DbSession
) -> BookingDetailOut:
    # 1. Валидируем пакет и вылет
    package = await db.get(Package, payload.package_id)
    if package is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Пакет не найден")
    departure = await db.get(Departure, payload.departure_id)
    if departure is None or departure.package_id != package.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Вылет не найден")

    partner = await db.get(Partner, package.partner_id)
    if partner is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Партнёр не найден")

    # 2. Валидируем паломников: все принадлежат клиенту
    res = await db.execute(
        select(Pilgrim).where(
            Pilgrim.id.in_(payload.pilgrim_ids), Pilgrim.customer_id == customer.id
        )
    )
    pilgrims = res.scalars().all()
    if len(pilgrims) != len(payload.pilgrim_ids):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Некоторые паломники не найдены")

    # 3. Валидируем размещения и считаем сумму
    pilgrim_by_id = {p.id: p for p in pilgrims}
    used_pilgrim_ids: set[UUID] = set()
    total = 0

    inv_map = {}
    inv_res = await db.execute(
        select(DepartureInventory).where(DepartureInventory.departure_id == departure.id)
    )
    for inv in inv_res.scalars().all():
        inv_map[inv.room_type] = inv

    placement_specs = []
    for pl in payload.placements:
        cap_required = _CAPACITY_BY_ROOM_TYPE[pl.room_type]
        if len(pl.pilgrim_ids) > cap_required:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"В комнату {pl.room_type.value} вместимостью {cap_required} нельзя поместить {len(pl.pilgrim_ids)} человек",
            )
        for pid in pl.pilgrim_ids:
            if pid not in pilgrim_by_id:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Паломник не указан в заявке")
            if pid in used_pilgrim_ids:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Паломник назначен в несколько комнат")
            used_pilgrim_ids.add(pid)

        # Махрам-проверка для FM-комнат с женщинами
        if pl.room_type in (RoomType.DBL_FM, RoomType.TRPL_FM, RoomType.QUAD_FM):
            for pid in pl.pilgrim_ids:
                pp = pilgrim_by_id[pid]
                if pp.gender == "F" and pp.mahram_pilgrim_id is None:
                    raise HTTPException(
                        status.HTTP_400_BAD_REQUEST,
                        f"Паломница {pp.full_name} без махрама не может быть размещена в FM-комнату",
                    )

        # Проверка инвентаря
        inv = inv_map.get(pl.room_type)
        if inv is None or not inv.is_enabled:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Тип размещения {pl.room_type.value} недоступен для вылета",
            )
        if (inv.sold + 1) > inv.capacity:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Нет мест в {pl.room_type.value} на этом вылете",
            )

        # Цена за человека: берём из вылета override или из пакета
        field = _price_field(pl.room_type)
        price_dep = getattr(departure, f"price_{field}")
        price_pkg = getattr(package, f"price_{field}")
        price = price_dep if price_dep is not None else price_pkg
        if price is None:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Не задана цена для {pl.room_type.value}",
            )
        placement_total = price * len(pl.pilgrim_ids)
        total += placement_total
        placement_specs.append({
            "room_type": pl.room_type,
            "capacity": cap_required,
            "price_per_person_uzs": price,
            "total_uzs": placement_total,
            "pilgrim_ids": pl.pilgrim_ids,
            "awaiting_co_lodger": len(pl.pilgrim_ids) < cap_required,
        })

    if used_pilgrim_ids != set(payload.pilgrim_ids):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Все паломники должны быть размещены")

    # 4. Создаём заявку
    code = await next_booking_code(db, partner)
    booking = Booking(
        code=code,
        partner_id=partner.id,
        customer_id=customer.id,
        package_id=package.id,
        departure_id=departure.id,
        source=payload.source,
        status=BookingStatus.NEW,
        sla_deadline_at=datetime.now(UTC) + timedelta(minutes=60),
        total_uzs=total,
        cashback_uzs=int(total * 0.003),  # 0.3% Click
    )
    db.add(booking)
    await db.flush()

    # 5. Размещения + booking_pilgrims
    for spec in placement_specs:
        placement = Placement(
            booking_id=booking.id,
            room_type=spec["room_type"],
            capacity=spec["capacity"],
            price_per_person_uzs=spec["price_per_person_uzs"],
            total_uzs=spec["total_uzs"],
            awaiting_co_lodger=spec["awaiting_co_lodger"],
        )
        db.add(placement)
        await db.flush()
        for pid in spec["pilgrim_ids"]:
            db.add(BookingPilgrim(
                booking_id=booking.id,
                pilgrim_id=pid,
                placement_id=placement.id,
            ))
        # Обновляем sold inventory
        inv = inv_map[spec["room_type"]]
        inv.sold += 1

    departure.sold_total += len(placement_specs)

    # 6. События
    db.add(BookingEvent(
        booking_id=booking.id,
        event_type="create",
        title="Заявка создана клиентом",
        description=f"Источник: {payload.source.value}",
        actor_kind="client",
        actor_id=customer.id,
        actor_name=customer.full_name or customer.phone,
    ))

    await audit(
        db, actor_kind="client", actor_id=customer.id, actor_name=customer.full_name,
        action=AuditAction.CREATE, object_kind="booking",
        object_id=booking.id, object_label=booking.code, scope_partner_id=partner.id,
    )

    await db.commit()
    await db.refresh(booking)
    return BookingDetailOut.model_validate(await _build_booking_detail(db, booking))


# ════════════ Клиент: свои заказы ════════════
@router.get("/me", response_model=Paginated[BookingOut])
async def list_my_bookings(
    customer: CurrentCustomer,
    db: DbSession,
    page: int = 1,
    page_size: int = 50,
    status_filter: BookingStatus | None = None,
) -> Paginated[BookingOut]:
    pp = PageParams(page=page, page_size=page_size)
    base = select(Booking).where(Booking.customer_id == customer.id)
    count_stmt = select(func.count(Booking.id)).where(Booking.customer_id == customer.id)
    if status_filter:
        base = base.where(Booking.status == status_filter)
        count_stmt = count_stmt.where(Booking.status == status_filter)
    total = (await db.execute(count_stmt)).scalar_one()
    res = await db.execute(base.order_by(Booking.created_at.desc()).offset(pp.offset).limit(pp.page_size))
    items = []
    for b in res.scalars().all():
        items.append(BookingOut.model_validate(await _build_booking_out(db, b)))
    return Paginated(items=items, total=total, page=pp.page, page_size=pp.page_size)


@router.get("/me/{booking_id}", response_model=BookingDetailOut)
async def get_my_booking(
    booking_id: UUID, customer: CurrentCustomer, db: DbSession
) -> BookingDetailOut:
    b = await db.get(Booking, booking_id)
    if b is None or b.customer_id != customer.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Заявка не найдена")
    return BookingDetailOut.model_validate(await _build_booking_detail(db, b))


# ════════════ Партнёр: список своих заявок ════════════
@router.get("/partner", response_model=Paginated[BookingOut])
async def list_partner_bookings(
    emp: CurrentPartnerEmployee,
    db: DbSession,
    page: int = 1,
    page_size: int = 50,
    status_filter: BookingStatus | None = None,
) -> Paginated[BookingOut]:
    pp = PageParams(page=page, page_size=page_size)
    base = select(Booking).where(Booking.partner_id == emp.partner_id)
    count_stmt = select(func.count(Booking.id)).where(Booking.partner_id == emp.partner_id)
    if status_filter:
        base = base.where(Booking.status == status_filter)
        count_stmt = count_stmt.where(Booking.status == status_filter)
    total = (await db.execute(count_stmt)).scalar_one()
    res = await db.execute(base.order_by(Booking.created_at.desc()).offset(pp.offset).limit(pp.page_size))
    items = []
    for b in res.scalars().all():
        items.append(BookingOut.model_validate(await _build_booking_out(db, b)))
    return Paginated(items=items, total=total, page=pp.page, page_size=pp.page_size)


@router.get("/partner/{booking_id}", response_model=BookingDetailOut)
async def get_partner_booking(
    booking_id: UUID, emp: CurrentPartnerEmployee, db: DbSession
) -> BookingDetailOut:
    b = await db.get(Booking, booking_id)
    if b is None or b.partner_id != emp.partner_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Заявка не найдена")
    return BookingDetailOut.model_validate(await _build_booking_detail(db, b))


@router.post("/partner/{booking_id}/confirm", response_model=BookingDetailOut)
async def confirm_booking(
    booking_id: UUID, emp: CurrentPartnerEmployee, db: DbSession
) -> BookingDetailOut:
    b = await db.get(Booking, booking_id)
    if b is None or b.partner_id != emp.partner_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Заявка не найдена")
    if b.status != BookingStatus.NEW:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Можно подтвердить только новую заявку")

    b.status = BookingStatus.KABUL
    b.confirmed_at = datetime.now(UTC)
    b.assigned_operator_id = emp.id

    db.add(BookingEvent(
        booking_id=b.id, event_type="confirm",
        title="Заявка подтверждена оператором",
        actor_kind="partner_employee", actor_id=emp.id, actor_name=emp.full_name,
    ))
    await audit(
        db, actor_kind="partner_employee", actor_id=emp.id, actor_name=emp.full_name,
        action=AuditAction.APPROVE, object_kind="booking",
        object_id=b.id, object_label=b.code, scope_partner_id=b.partner_id,
    )
    await db.commit()
    await db.refresh(b)
    return BookingDetailOut.model_validate(await _build_booking_detail(db, b))


@router.post("/partner/{booking_id}/reject", response_model=BookingDetailOut)
async def reject_booking(
    booking_id: UUID,
    payload: BookingRejectIn,
    emp: CurrentPartnerEmployee,
    db: DbSession,
) -> BookingDetailOut:
    b = await db.get(Booking, booking_id)
    if b is None or b.partner_id != emp.partner_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Заявка не найдена")
    if b.status not in (BookingStatus.NEW, BookingStatus.KABUL, BookingStatus.PROCESSING):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Заявку нельзя отменить в текущем статусе")

    b.status = BookingStatus.CANCELLED
    b.cancelled_at = datetime.now(UTC)
    b.cancellation_reason_id = payload.reason_id
    b.cancellation_comment = payload.comment

    # Возвращаем места в inventory
    inv_res = await db.execute(
        select(DepartureInventory).where(DepartureInventory.departure_id == b.departure_id)
    )
    inv_map = {i.room_type: i for i in inv_res.scalars().all()}
    pls = (await db.execute(
        select(Placement).where(Placement.booking_id == b.id)
    )).scalars().all()
    departure = await db.get(Departure, b.departure_id)
    for pl in pls:
        inv = inv_map.get(pl.room_type)
        if inv and inv.sold > 0:
            inv.sold -= 1
        if departure and departure.sold_total > 0:
            departure.sold_total -= 1

    db.add(BookingEvent(
        booking_id=b.id, event_type="cancel",
        title="Заявка отменена партнёром",
        description=payload.comment,
        actor_kind="partner_employee", actor_id=emp.id, actor_name=emp.full_name,
    ))
    await audit(
        db, actor_kind="partner_employee", actor_id=emp.id, actor_name=emp.full_name,
        action=AuditAction.REJECT, object_kind="booking",
        object_id=b.id, object_label=b.code, scope_partner_id=b.partner_id,
        description=payload.comment,
    )
    await db.commit()
    await db.refresh(b)
    return BookingDetailOut.model_validate(await _build_booking_detail(db, b))


@router.post("/partner/{booking_id}/complete", response_model=BookingDetailOut)
async def complete_booking(
    booking_id: UUID, emp: CurrentPartnerEmployee, db: DbSession
) -> BookingDetailOut:
    b = await db.get(Booking, booking_id)
    if b is None or b.partner_id != emp.partner_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Заявка не найдена")
    if b.status != BookingStatus.KABUL:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Завершить можно только подтверждённую заявку")

    b.status = BookingStatus.COMPLETED
    b.completed_at = datetime.now(UTC)
    db.add(BookingEvent(
        booking_id=b.id, event_type="complete",
        title="Тур завершён",
        actor_kind="partner_employee", actor_id=emp.id, actor_name=emp.full_name,
    ))
    await db.commit()
    await db.refresh(b)
    return BookingDetailOut.model_validate(await _build_booking_detail(db, b))


# ════════════ Платформа: чтение всех заявок ════════════
@router.get("/", response_model=Paginated[BookingOut])
async def list_all_bookings(
    db: DbSession,
    _: CurrentUmrabor,
    page: int = 1,
    page_size: int = 50,
    status_filter: BookingStatus | None = None,
) -> Paginated[BookingOut]:
    pp = PageParams(page=page, page_size=page_size)
    base = select(Booking)
    count_stmt = select(func.count(Booking.id))
    if status_filter:
        base = base.where(Booking.status == status_filter)
        count_stmt = count_stmt.where(Booking.status == status_filter)
    total = (await db.execute(count_stmt)).scalar_one()
    res = await db.execute(base.order_by(Booking.created_at.desc()).offset(pp.offset).limit(pp.page_size))
    items = []
    for b in res.scalars().all():
        items.append(BookingOut.model_validate(await _build_booking_out(db, b)))
    return Paginated(items=items, total=total, page=pp.page, page_size=pp.page_size)


@router.get("/{booking_id}", response_model=BookingDetailOut)
async def get_booking(
    booking_id: UUID, db: DbSession, _: CurrentUmrabor
) -> BookingDetailOut:
    b = await db.get(Booking, booking_id)
    if b is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Заявка не найдена")
    return BookingDetailOut.model_validate(await _build_booking_detail(db, b))


# ════════════ Mock-Click оплата ════════════
@router.post("/me/{booking_id}/pay-mock", response_model=BookingDetailOut)
async def mock_click_pay(
    booking_id: UUID, customer: CurrentCustomer, db: DbSession
) -> BookingDetailOut:
    """Имитация оплаты через Click. Создаёт Payment + отмечает заявку как оплаченную."""
    b = await db.get(Booking, booking_id)
    if b is None or b.customer_id != customer.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Заявка не найдена")
    if b.status != BookingStatus.NEW:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Заявка уже обработана")

    payment_code = await next_payment_code(db)
    payment = Payment(
        code=payment_code,
        booking_id=b.id,
        customer_id=customer.id,
        partner_id=b.partner_id,
        channel=PaymentChannel.CLICK,
        amount_uzs=b.total_uzs,
        status=PaymentStatus.SUCCESS,
        click_trans_id=payment_code,
        click_phone=customer.phone,
        paid_at=datetime.now(UTC),
        raw={"mock": True},
    )
    db.add(payment)

    db.add(BookingEvent(
        booking_id=b.id, event_type="payment",
        title="Оплачено через Click",
        description=f"{payment_code}: {b.total_uzs:,} сум",
        actor_kind="system",
    ))
    await db.commit()
    await db.refresh(b)
    return BookingDetailOut.model_validate(await _build_booking_detail(db, b))


# silence unused selectinload import
_ = selectinload
