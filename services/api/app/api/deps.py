"""Общие FastAPI-зависимости: DB сессия + текущий пользователь по JWT."""

from collections.abc import AsyncGenerator
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import JWTError, decode_token
from app.db.session import AsyncSessionLocal
from app.models import Customer, PartnerEmployee, UserUmrabor
from app.models.enums import PartnerRole, UmraborRole

bearer = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


DbSession = Annotated[AsyncSession, Depends(get_db)]


class AuthSubject:
    """Информация о текущем субъекте, извлечённая из JWT."""

    def __init__(self, sub_id: UUID, sub_type: str, payload: dict):
        self.id = sub_id
        self.kind = sub_type
        self.payload = payload


def _credentials_exception(detail: str = "Не авторизовано") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_subject(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> AuthSubject:
    if creds is None:
        raise _credentials_exception()
    try:
        payload = decode_token(creds.credentials)
    except JWTError as e:
        raise _credentials_exception("Невалидный токен") from e

    if payload.get("type") != "access":
        raise _credentials_exception("Ожидался access-токен")

    sub = payload.get("sub")
    sub_type = payload.get("sub_type")
    if not sub or sub_type not in ("umrabor", "partner", "client"):
        raise _credentials_exception("Невалидный subject")

    return AuthSubject(sub_id=UUID(sub), sub_type=sub_type, payload=payload)


CurrentSubject = Annotated[AuthSubject, Depends(get_current_subject)]


# ─── UMRABOR ───
async def get_umrabor_user(
    subject: CurrentSubject,
    db: DbSession,
) -> UserUmrabor:
    if subject.kind != "umrabor":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Доступ только для сотрудников UMRABOR")
    user = await db.get(UserUmrabor, subject.id)
    if user is None or not user.is_active:
        raise _credentials_exception("Пользователь отключён или удалён")
    return user


CurrentUmrabor = Annotated[UserUmrabor, Depends(get_umrabor_user)]


async def require_umrabor_super(user: CurrentUmrabor) -> UserUmrabor:
    if user.role != UmraborRole.SUPER_ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Требуется роль Super-admin")
    return user


CurrentUmraborSuper = Annotated[UserUmrabor, Depends(require_umrabor_super)]


# ─── Партнёр ───
async def get_partner_employee(
    subject: CurrentSubject,
    db: DbSession,
) -> PartnerEmployee:
    if subject.kind != "partner":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Доступ только для сотрудников партнёра")
    emp = await db.get(PartnerEmployee, subject.id)
    if emp is None or not emp.is_active:
        raise _credentials_exception("Сотрудник отключён или удалён")
    return emp


CurrentPartnerEmployee = Annotated[PartnerEmployee, Depends(get_partner_employee)]


async def require_partner_admin(emp: CurrentPartnerEmployee) -> PartnerEmployee:
    if emp.role != PartnerRole.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Требуется роль Админ партнёра")
    return emp


CurrentPartnerAdmin = Annotated[PartnerEmployee, Depends(require_partner_admin)]


# ─── Клиент ───
async def get_customer(
    subject: CurrentSubject,
    db: DbSession,
) -> Customer:
    if subject.kind != "client":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Доступ только для клиентов")
    res = await db.execute(select(Customer).where(Customer.id == subject.id))
    customer = res.scalar_one_or_none()
    if customer is None:
        raise _credentials_exception("Клиент не найден")
    return customer


CurrentCustomer = Annotated[Customer, Depends(get_customer)]
