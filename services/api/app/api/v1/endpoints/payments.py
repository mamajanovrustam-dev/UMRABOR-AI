"""Платежи: read-only лента (Платформа + Партнёр)."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select

from app.api.deps import CurrentPartnerEmployee, CurrentUmrabor, DbSession
from app.models import Booking, Customer, Partner, Payment
from app.models.enums import PaymentStatus
from app.schemas.common import PageParams, Paginated
from app.schemas.common import BaseSchema
from datetime import datetime
from app.models.enums import PaymentChannel


class PaymentOut(BaseSchema):
    id: UUID
    code: str
    booking_id: UUID
    booking_code: str | None = None
    customer_id: UUID
    customer_name: str | None = None
    customer_phone: str | None = None
    partner_id: UUID
    partner_brand: str | None = None
    channel: PaymentChannel
    amount_uzs: int
    status: PaymentStatus
    paid_at: datetime | None = None
    refund_at: datetime | None = None
    created_at: datetime


router = APIRouter()


async def _enrich(db, p: Payment) -> PaymentOut:
    booking = await db.get(Booking, p.booking_id)
    customer = await db.get(Customer, p.customer_id)
    partner = await db.get(Partner, p.partner_id)
    return PaymentOut(
        id=p.id, code=p.code,
        booking_id=p.booking_id, booking_code=booking.code if booking else None,
        customer_id=p.customer_id,
        customer_name=customer.full_name if customer else None,
        customer_phone=customer.phone if customer else None,
        partner_id=p.partner_id, partner_brand=partner.brand if partner else None,
        channel=p.channel, amount_uzs=p.amount_uzs,
        status=p.status, paid_at=p.paid_at, refund_at=p.refund_at,
        created_at=p.created_at,
    )


@router.get("/", response_model=Paginated[PaymentOut])
async def list_all_payments(
    db: DbSession,
    _: CurrentUmrabor,
    page: int = 1,
    page_size: int = 50,
    status_filter: PaymentStatus | None = None,
) -> Paginated[PaymentOut]:
    pp = PageParams(page=page, page_size=page_size)
    base = select(Payment)
    cs = select(func.count(Payment.id))
    if status_filter:
        base = base.where(Payment.status == status_filter)
        cs = cs.where(Payment.status == status_filter)
    total = (await db.execute(cs)).scalar_one()
    res = await db.execute(base.order_by(Payment.created_at.desc()).offset(pp.offset).limit(pp.page_size))
    items = [await _enrich(db, p) for p in res.scalars().all()]
    return Paginated(items=items, total=total, page=pp.page, page_size=pp.page_size)


@router.get("/partner", response_model=Paginated[PaymentOut])
async def list_partner_payments(
    emp: CurrentPartnerEmployee,
    db: DbSession,
    page: int = 1,
    page_size: int = 50,
) -> Paginated[PaymentOut]:
    pp = PageParams(page=page, page_size=page_size)
    base = select(Payment).where(Payment.partner_id == emp.partner_id)
    cs = select(func.count(Payment.id)).where(Payment.partner_id == emp.partner_id)
    total = (await db.execute(cs)).scalar_one()
    res = await db.execute(base.order_by(Payment.created_at.desc()).offset(pp.offset).limit(pp.page_size))
    items = [await _enrich(db, p) for p in res.scalars().all()]
    return Paginated(items=items, total=total, page=pp.page, page_size=pp.page_size)


@router.get("/{payment_id}", response_model=PaymentOut)
async def get_payment(
    payment_id: UUID, db: DbSession, _: CurrentUmrabor
) -> PaymentOut:
    p = await db.get(Payment, payment_id)
    if p is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Платёж не найден")
    return await _enrich(db, p)
