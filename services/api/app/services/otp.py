"""Генерация и проверка одноразовых кодов для phone-OTP."""

import secrets
from datetime import UTC, datetime, timedelta

from passlib.context import CryptContext
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import OtpCode
from app.services.sms import sms

_hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")

OTP_TTL_MIN = 5
OTP_MAX_ATTEMPTS = 5


def _generate_code() -> str:
    """В dev возвращаем 0000 — чтобы было легко тестировать. В prod — 6 цифр."""
    if settings.ENV in ("development", "test"):
        return "0000"
    return f"{secrets.randbelow(1_000_000):06d}"


async def issue_otp(db: AsyncSession, phone: str, purpose: str = "login") -> str:
    code = _generate_code()
    code_hash = _hasher.hash(code)
    expires_at = datetime.now(UTC) + timedelta(minutes=OTP_TTL_MIN)

    otp = OtpCode(
        phone=phone,
        code_hash=code_hash,
        expires_at=expires_at,
        purpose=purpose,
    )
    db.add(otp)
    await db.flush()

    await sms.send(
        phone,
        f"UMRABOR: код подтверждения {code}. Не сообщайте никому. Действует {OTP_TTL_MIN} мин.",
    )
    return code


async def verify_otp(db: AsyncSession, phone: str, code: str) -> bool:
    res = await db.execute(
        select(OtpCode)
        .where(OtpCode.phone == phone, OtpCode.used_at.is_(None))
        .order_by(OtpCode.created_at.desc())
        .limit(1)
    )
    otp = res.scalar_one_or_none()
    if otp is None:
        return False
    if otp.attempts >= OTP_MAX_ATTEMPTS:
        return False
    if otp.expires_at < datetime.now(UTC):
        return False

    otp.attempts += 1
    ok = _hasher.verify(code, otp.code_hash)
    if ok:
        await db.execute(
            update(OtpCode).where(OtpCode.id == otp.id).values(used_at=datetime.now(UTC))
        )
    await db.flush()
    return ok
