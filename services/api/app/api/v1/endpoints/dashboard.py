"""Dashboards: KPI для Платформы и Партнёра."""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter
from sqlalchemy import func, select

from app.api.deps import CurrentPartnerEmployee, CurrentUmrabor, DbSession
from app.models import Booking, Package, Partner, Payment
from app.models.enums import BookingStatus, PackageStatus, PartnerStatus
from app.schemas.common import BaseSchema


class KpiPlatform(BaseSchema):
    gmv_7d_uzs: int
    active_partners: int
    published_packages: int
    total_packages: int
    bookings_7d: int
    confirm_rate_pct: float
    payments_7d_uzs: int


class KpiPartner(BaseSchema):
    sales_today: int
    sales_7d: int
    revenue_7d_uzs: int
    new_bookings: int
    confirm_rate_pct: float
    cancel_rate_pct: float


router = APIRouter()


@router.get("/platform", response_model=KpiPlatform)
async def platform_kpi(db: DbSession, _: CurrentUmrabor) -> KpiPlatform:
    week_ago = datetime.now(UTC) - timedelta(days=7)

    gmv = (await db.execute(
        select(func.coalesce(func.sum(Payment.amount_uzs), 0))
        .where(Payment.paid_at >= week_ago)
    )).scalar_one()

    active_partners = (await db.execute(
        select(func.count(Partner.id)).where(Partner.status == PartnerStatus.ACTIVE)
    )).scalar_one()

    published = (await db.execute(
        select(func.count(Package.id)).where(Package.status == PackageStatus.PUBLISHED)
    )).scalar_one()
    total_packages = (await db.execute(select(func.count(Package.id)))).scalar_one()

    total_bookings_7d = (await db.execute(
        select(func.count(Booking.id)).where(Booking.created_at >= week_ago)
    )).scalar_one()
    confirmed_7d = (await db.execute(
        select(func.count(Booking.id)).where(
            Booking.created_at >= week_ago,
            Booking.status.in_([BookingStatus.KABUL, BookingStatus.COMPLETED]),
        )
    )).scalar_one()
    confirm_rate = (confirmed_7d / total_bookings_7d * 100) if total_bookings_7d else 0.0

    payments_7d = (await db.execute(
        select(func.coalesce(func.sum(Payment.amount_uzs), 0))
        .where(Payment.created_at >= week_ago)
    )).scalar_one()

    return KpiPlatform(
        gmv_7d_uzs=gmv,
        active_partners=active_partners,
        published_packages=published,
        total_packages=total_packages,
        bookings_7d=total_bookings_7d,
        confirm_rate_pct=round(confirm_rate, 1),
        payments_7d_uzs=payments_7d,
    )


@router.get("/partner", response_model=KpiPartner)
async def partner_kpi(emp: CurrentPartnerEmployee, db: DbSession) -> KpiPartner:
    today = datetime.now(UTC).date()
    week_ago = datetime.now(UTC) - timedelta(days=7)

    sales_today = (await db.execute(
        select(func.count(Booking.id)).where(
            Booking.partner_id == emp.partner_id,
            func.date(Booking.created_at) == today,
        )
    )).scalar_one()
    sales_7d = (await db.execute(
        select(func.count(Booking.id)).where(
            Booking.partner_id == emp.partner_id,
            Booking.created_at >= week_ago,
        )
    )).scalar_one()
    revenue_7d = (await db.execute(
        select(func.coalesce(func.sum(Payment.amount_uzs), 0)).where(
            Payment.partner_id == emp.partner_id,
            Payment.paid_at >= week_ago,
        )
    )).scalar_one()
    new_bookings = (await db.execute(
        select(func.count(Booking.id)).where(
            Booking.partner_id == emp.partner_id,
            Booking.status == BookingStatus.NEW,
        )
    )).scalar_one()

    confirmed = (await db.execute(
        select(func.count(Booking.id)).where(
            Booking.partner_id == emp.partner_id,
            Booking.created_at >= week_ago,
            Booking.status.in_([BookingStatus.KABUL, BookingStatus.COMPLETED]),
        )
    )).scalar_one()
    cancelled = (await db.execute(
        select(func.count(Booking.id)).where(
            Booking.partner_id == emp.partner_id,
            Booking.created_at >= week_ago,
            Booking.status == BookingStatus.CANCELLED,
        )
    )).scalar_one()

    confirm_rate = (confirmed / sales_7d * 100) if sales_7d else 0.0
    cancel_rate = (cancelled / sales_7d * 100) if sales_7d else 0.0

    return KpiPartner(
        sales_today=sales_today,
        sales_7d=sales_7d,
        revenue_7d_uzs=revenue_7d,
        new_bookings=new_bookings,
        confirm_rate_pct=round(confirm_rate, 1),
        cancel_rate_pct=round(cancel_rate, 1),
    )
