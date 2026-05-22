"""Реестр паломников клиента + махрам-связи."""

from datetime import date as _date
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentCustomer, CurrentPartnerEmployee, DbSession
from app.models import Booking, BookingPilgrim, Pilgrim
from app.models.enums import DocumentType, Gender, MahramRelation
from app.schemas.common import BaseSchema, OkResponse
from datetime import datetime


class PilgrimOut(BaseSchema):
    id: UUID
    customer_id: UUID
    last_name: str
    first_name: str
    middle_name: str | None = None
    full_name: str
    gender: Gender
    birth_date: _date
    avatar_url: str | None = None
    document_type: DocumentType
    document_series_number: str | None = None
    document_valid_until: _date | None = None
    document_file_url: str | None = None
    mahram_pilgrim_id: UUID | None = None
    mahram_relation: MahramRelation | None = None
    notes: str | None = None
    created_at: datetime


class PilgrimCreate(BaseSchema):
    last_name: str
    first_name: str
    middle_name: str | None = None
    gender: Gender
    birth_date: _date
    document_type: DocumentType = DocumentType.ZAGRAN
    document_series_number: str | None = None
    document_valid_until: _date | None = None
    mahram_pilgrim_id: UUID | None = None
    mahram_relation: MahramRelation | None = None


class PilgrimUpdate(PilgrimCreate):
    pass


router = APIRouter()


@router.get("/me", response_model=list[PilgrimOut])
async def list_my_pilgrims(customer: CurrentCustomer, db: DbSession) -> list[PilgrimOut]:
    res = await db.execute(
        select(Pilgrim).where(Pilgrim.customer_id == customer.id).order_by(Pilgrim.full_name)
    )
    return [PilgrimOut.model_validate(p) for p in res.scalars().all()]


@router.post("/me", response_model=PilgrimOut, status_code=status.HTTP_201_CREATED)
async def create_my_pilgrim(
    payload: PilgrimCreate, customer: CurrentCustomer, db: DbSession
) -> PilgrimOut:
    # Валидация махрама: если указан — должен принадлежать тому же клиенту и быть мужчиной
    if payload.mahram_pilgrim_id:
        mp = await db.get(Pilgrim, payload.mahram_pilgrim_id)
        if mp is None or mp.customer_id != customer.id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Махрам не найден")
        if mp.gender != Gender.MALE:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Махрам должен быть мужчиной")

    data = payload.model_dump()
    full = " ".join(filter(None, [data["last_name"], data["first_name"], data.get("middle_name")]))
    p = Pilgrim(customer_id=customer.id, full_name=full, **data)
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return PilgrimOut.model_validate(p)


@router.put("/me/{pilgrim_id}", response_model=PilgrimOut)
async def update_my_pilgrim(
    pilgrim_id: UUID,
    payload: PilgrimUpdate,
    customer: CurrentCustomer,
    db: DbSession,
) -> PilgrimOut:
    p = await db.get(Pilgrim, pilgrim_id)
    if p is None or p.customer_id != customer.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Паломник не найден")
    if payload.mahram_pilgrim_id:
        mp = await db.get(Pilgrim, payload.mahram_pilgrim_id)
        if mp is None or mp.customer_id != customer.id or mp.id == p.id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Невалидный махрам")
        if mp.gender != Gender.MALE:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Махрам должен быть мужчиной")
    data = payload.model_dump()
    for k, v in data.items():
        setattr(p, k, v)
    p.full_name = " ".join(filter(None, [p.last_name, p.first_name, p.middle_name]))
    await db.commit()
    await db.refresh(p)
    return PilgrimOut.model_validate(p)


@router.delete("/me/{pilgrim_id}", response_model=OkResponse)
async def delete_my_pilgrim(
    pilgrim_id: UUID, customer: CurrentCustomer, db: DbSession
) -> OkResponse:
    p = await db.get(Pilgrim, pilgrim_id)
    if p is None or p.customer_id != customer.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Паломник не найден")
    # Проверка — нет ли активных заявок
    res = await db.execute(
        select(BookingPilgrim.id).join(Booking, BookingPilgrim.booking_id == Booking.id)
        .where(BookingPilgrim.pilgrim_id == p.id)
    )
    if res.first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Паломник используется в заявках")
    await db.delete(p)
    await db.commit()
    return OkResponse(message="Паломник удалён")


# ════════════ Партнёр: реестр паломников по своим заявкам ════════════
@router.get("/partner", response_model=list[PilgrimOut])
async def list_partner_pilgrims(
    emp: CurrentPartnerEmployee, db: DbSession
) -> list[PilgrimOut]:
    """Все паломники, которые ездили/едут в заявках этого партнёра."""
    res = await db.execute(
        select(Pilgrim)
        .join(BookingPilgrim, BookingPilgrim.pilgrim_id == Pilgrim.id)
        .join(Booking, BookingPilgrim.booking_id == Booking.id)
        .where(Booking.partner_id == emp.partner_id)
        .distinct()
        .order_by(Pilgrim.full_name)
    )
    return [PilgrimOut.model_validate(p) for p in res.scalars().all()]
