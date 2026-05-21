"""JWT и хеширование паролей. Поддержка 3 типов субъектов: umrabor / partner / client."""

from datetime import UTC, datetime, timedelta
from typing import Any, Literal
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

SubjectType = Literal["umrabor", "partner", "client"]

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return _pwd.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd.verify(plain, hashed)


def _build_token(
    *,
    sub: str,
    sub_type: SubjectType,
    token_type: Literal["access", "refresh"],
    ttl: timedelta,
    extra: dict[str, Any] | None = None,
) -> str:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": sub,
        "sub_type": sub_type,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + ttl).timestamp()),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(
    sub: str | UUID,
    sub_type: SubjectType,
    extra: dict[str, Any] | None = None,
) -> str:
    return _build_token(
        sub=str(sub),
        sub_type=sub_type,
        token_type="access",
        ttl=timedelta(minutes=settings.ACCESS_TOKEN_TTL_MIN),
        extra=extra,
    )


def create_refresh_token(sub: str | UUID, sub_type: SubjectType) -> str:
    return _build_token(
        sub=str(sub),
        sub_type=sub_type,
        token_type="refresh",
        ttl=timedelta(days=settings.REFRESH_TOKEN_TTL_DAYS),
    )


def decode_token(token: str) -> dict[str, Any]:
    """Декодирует и валидирует JWT. Возвращает payload или бросает JWTError."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


__all__ = [
    "JWTError",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "hash_password",
    "verify_password",
]
