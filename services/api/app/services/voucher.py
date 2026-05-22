"""Генерация PDF-ваучеров через WeasyPrint. По одному на паломника."""

import io
import logging
from uuid import UUID

import boto3
from botocore.exceptions import ClientError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import (
    Airline,
    Booking,
    BookingPilgrim,
    Customer,
    Departure,
    Hotel,
    Package,
    PackageHotel,
    Partner,
    Pilgrim,
    Placement,
)

log = logging.getLogger(__name__)


_VOUCHER_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>UMRABOR · Ваучер {booking_code}</title>
  <style>
    @page {{ size: A4; margin: 18mm 16mm; }}
    body {{ font-family: 'DejaVu Sans', sans-serif; color: #1A1A2E; line-height: 1.4; }}
    .brand {{ font-size: 28px; font-weight: 700; letter-spacing: 2px; }}
    .brand .gold {{ color: #C9A84C; }}
    .h1 {{ font-size: 22px; margin: 8px 0 0; }}
    .sub {{ color: #7A7A8C; font-size: 12px; }}
    .code {{ font-family: 'DejaVu Sans Mono', monospace; font-weight: 700; color: #C9A84C; font-size: 14px; }}
    .row {{ display: flex; justify-content: space-between; align-items: center; margin: 14px 0; }}
    .card {{ border: 1px solid #EDE8DC; border-radius: 8px; padding: 14px; margin-top: 10px; }}
    .kv {{ display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px dashed #EDE8DC; font-size: 13px; }}
    .kv:last-child {{ border-bottom: 0; }}
    .label {{ color: #7A7A8C; }}
    .val {{ font-weight: 600; }}
    .footer {{ margin-top: 30px; font-size: 10px; color: #7A7A8C; text-align: center; }}
    .badge {{ display: inline-block; background: #C9A84C; color: #fff; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }}
  </style>
</head>
<body>
  <div class="row">
    <div class="brand">UMRA<span class="gold">BOR</span></div>
    <div class="sub">Ваучер · {booking_code}</div>
  </div>

  <div class="h1">{package_name}</div>
  <div class="sub">{partner_brand} · Лицензия № {partner_license}</div>

  <div class="card">
    <div class="kv"><span class="label">Паломник</span><span class="val">{pilgrim_name}</span></div>
    <div class="kv"><span class="label">Документ</span><span class="val">{document}</span></div>
    <div class="kv"><span class="label">Маршрут</span><span class="val">{route}</span></div>
    <div class="kv"><span class="label">Длительность</span><span class="val">{duration} дн</span></div>
    <div class="kv"><span class="label">Вылет туда</span><span class="val">{date_out} · {flight_out}</span></div>
    <div class="kv"><span class="label">Вылет обратно</span><span class="val">{date_in} · {flight_in}</span></div>
    <div class="kv"><span class="label">Авиакомпания</span><span class="val">{airline}</span></div>
    <div class="kv"><span class="label">Размещение</span><span class="val">{room_type}</span></div>
  </div>

  <div class="card">
    <div class="kv"><span class="label">Отели</span><span class="val">{hotels}</span></div>
  </div>

  <div style="margin-top: 24px; text-align: right;">
    <span class="badge">Оплачено через Click</span>
  </div>

  <div class="footer">
    Этот ваучер подтверждает участие паломника в туре UMRABOR.
    Предъявите при регистрации на рейс и check-in в отеле.<br>
    UMRABOR LLC · Лицензия № UMR-001 · Тошкент · umrabor.uz
  </div>
</body>
</html>
"""


def _s3_client():
    return boto3.client(
        "s3",
        endpoint_url=str(settings.S3_ENDPOINT),
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
    )


def _ensure_bucket(s3, bucket: str) -> None:
    try:
        s3.head_bucket(Bucket=bucket)
    except ClientError:
        s3.create_bucket(Bucket=bucket)


async def generate_voucher_pdf(db: AsyncSession, booking_id: UUID) -> tuple[bytes, str]:
    """Возвращает (pdf_bytes, filename) для первой PDF-ваучера заказа.

    В реальном production здесь будет генерироваться отдельный ваучер на каждого паломника
    и пакетный ZIP. Для v1 — один PDF на заявку (для всех паломников).
    """
    from weasyprint import HTML  # отложенный импорт чтобы не тормозить старт API

    b = await db.get(Booking, booking_id)
    if b is None:
        raise ValueError("Booking not found")
    partner = await db.get(Partner, b.partner_id)
    package = await db.get(Package, b.package_id)
    departure = await db.get(Departure, b.departure_id)
    customer = await db.get(Customer, b.customer_id)
    airline = (
        await db.get(Airline, package.airline_id) if package and package.airline_id else None
    )

    # Hotels list
    hotel_rows = (
        await db.execute(
            select(PackageHotel, Hotel)
            .join(Hotel, PackageHotel.hotel_id == Hotel.id)
            .where(PackageHotel.package_id == package.id)
            .order_by(PackageHotel.sort_order)
        )
    ).all()
    hotels_str = " · ".join(f"{h.name} ({ph.nights}д)" for ph, h in hotel_rows) or "—"

    # Pilgrims + placements
    bp_rows = (
        await db.execute(
            select(BookingPilgrim, Pilgrim, Placement)
            .join(Pilgrim, BookingPilgrim.pilgrim_id == Pilgrim.id)
            .outerjoin(Placement, BookingPilgrim.placement_id == Placement.id)
            .where(BookingPilgrim.booking_id == b.id)
        )
    ).all()

    pilgrim_blocks = []
    for _bp, p, pl in bp_rows:
        pilgrim_blocks.append(
            _VOUCHER_HTML.format(
                booking_code=b.code,
                package_name=package.name if package else "—",
                partner_brand=partner.brand if partner else "—",
                partner_license=partner.license_no if partner else "—",
                pilgrim_name=p.full_name,
                document=f"{p.document_type.upper()} {p.document_series_number or '—'}",
                route=" → ".join(package.route) if package and package.route else "—",
                duration=package.duration_days if package else "—",
                date_out=departure.date_out.isoformat() if departure else "—",
                date_in=departure.date_in.isoformat() if departure else "—",
                flight_out=departure.flight_out or "—" if departure else "—",
                flight_in=departure.flight_in or "—" if departure else "—",
                airline=airline.name if airline else "—",
                room_type=pl.room_type if pl else "—",
                hotels=hotels_str,
            )
        )

    # WeasyPrint: одна страница на паломника
    full_html = "<div style='page-break-after: always;'></div>".join(pilgrim_blocks)
    pdf_bytes = HTML(string=full_html).write_pdf()

    filename = f"voucher-{b.code}.pdf"

    # Сохраняем в MinIO
    try:
        s3 = _s3_client()
        _ensure_bucket(s3, settings.S3_BUCKET_VOUCHERS)
        s3.put_object(
            Bucket=settings.S3_BUCKET_VOUCHERS,
            Key=filename,
            Body=pdf_bytes,
            ContentType="application/pdf",
        )
        voucher_url = f"{settings.S3_PUBLIC_URL}/{settings.S3_BUCKET_VOUCHERS}/{filename}"
        b.voucher_url = voucher_url
        await db.commit()
    except Exception as e:  # noqa: BLE001
        log.warning("Не удалось загрузить ваучер в S3: %s", e)

    # Также возвращаем bytes для прямой отдачи
    _ = customer  # not used in current template
    _ = io  # reserved for future zipping
    return pdf_bytes, filename
