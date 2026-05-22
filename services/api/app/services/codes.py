"""Генерация человекочитаемых ID: UM-2026-0061, TR-7842919."""

import secrets
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Booking, Partner, Payment

_PREFIX_BY_BRAND = {
    "Ramaz Travel": "UM",
    "Safar Tours": "SF",
    "Barakah VIP": "BR",
    "Nur Travel": "NT",
    "Hajj.uz": "HT",
    "Umra Premium": "UP",
}


def _prefix_for(brand: str) -> str:
    return _PREFIX_BY_BRAND.get(brand, "UM")


async def next_booking_code(db: AsyncSession, partner: Partner) -> str:
    """Формат: {PREFIX}-{YYYY}-{NNNN} (последовательный номер за год)."""
    prefix = _prefix_for(partner.brand)
    year = datetime.now(UTC).year
    pattern = f"{prefix}-{year}-%"
    res = await db.execute(
        select(func.count(Booking.id)).where(Booking.code.like(pattern))
    )
    existing = res.scalar_one() or 0
    return f"{prefix}-{year}-{existing + 1:04d}"


async def next_payment_code(db: AsyncSession) -> str:
    """TR-XXXXXXX (7 цифр)."""
    while True:
        candidate = f"TR-{secrets.randbelow(10_000_000):07d}"
        res = await db.execute(select(Payment).where(Payment.code == candidate).limit(1))
        if res.scalar_one_or_none() is None:
            return candidate
