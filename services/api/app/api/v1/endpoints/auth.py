"""Auth endpoints для 3 типов субъектов: UMRABOR / Партнёр / Клиент."""

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import (
    CurrentCustomer,
    CurrentPartnerEmployee,
    CurrentUmrabor,
    DbSession,
)
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.models import Customer, PartnerEmployee, UserUmrabor
from app.schemas.auth import (
    CustomerClickAuthIn,
    CustomerLoginOut,
    CustomerMe,
    CustomerOtpRequestIn,
    CustomerOtpRequestOut,
    CustomerOtpVerifyIn,
    PartnerChangePasswordIn,
    PartnerLoginIn,
    PartnerLoginOut,
    PartnerMe,
    TokenPair,
    UmraborLoginIn,
    UmraborLoginOut,
    UmraborMe,
)
from app.schemas.common import OkResponse
from app.services.otp import issue_otp, verify_otp

router = APIRouter()


def _issue_tokens(sub_id, sub_type: str) -> TokenPair:
    return TokenPair(
        access_token=create_access_token(sub_id, sub_type),  # type: ignore[arg-type]
        refresh_token=create_refresh_token(sub_id, sub_type),  # type: ignore[arg-type]
        expires_in=settings.ACCESS_TOKEN_TTL_MIN * 60,
    )


# ════════════ UMRABOR ════════════
@router.post("/umrabor/login", response_model=UmraborLoginOut)
async def umrabor_login(payload: UmraborLoginIn, db: DbSession) -> UmraborLoginOut:
    res = await db.execute(select(UserUmrabor).where(UserUmrabor.login == payload.login))
    user = res.scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Неверный логин или пароль")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Аккаунт отключён")

    user.last_login_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(user)

    return UmraborLoginOut(
        tokens=_issue_tokens(user.id, "umrabor"),
        user=UmraborMe.model_validate(user),
    )


@router.get("/umrabor/me", response_model=UmraborMe)
async def umrabor_me(user: CurrentUmrabor) -> UmraborMe:
    return UmraborMe.model_validate(user)


# ════════════ Партнёр ════════════
@router.post("/partner/login", response_model=PartnerLoginOut)
async def partner_login(payload: PartnerLoginIn, db: DbSession) -> PartnerLoginOut:
    res = await db.execute(select(PartnerEmployee).where(PartnerEmployee.login == payload.login))
    emp = res.scalar_one_or_none()
    if emp is None or not verify_password(payload.password, emp.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Неверный логин или пароль")
    if not emp.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Аккаунт отключён")

    emp.last_login_at = datetime.now(UTC)
    await db.commit()

    # Загружаем партнёра для brand-метки
    from app.models import Partner

    partner = await db.get(Partner, emp.partner_id)

    return PartnerLoginOut(
        tokens=_issue_tokens(emp.id, "partner"),
        user=PartnerMe(
            id=emp.id,
            partner_id=emp.partner_id,
            partner_brand=partner.brand if partner else "",
            login=emp.login,
            full_name=emp.full_name,
            email=emp.email,
            phone=emp.phone,
            role=emp.role,
            is_active=emp.is_active,
            must_change_password=emp.must_change_password,
            last_login_at=emp.last_login_at,
        ),
    )


@router.get("/partner/me", response_model=PartnerMe)
async def partner_me(emp: CurrentPartnerEmployee, db: DbSession) -> PartnerMe:
    from app.models import Partner

    partner = await db.get(Partner, emp.partner_id)
    return PartnerMe(
        id=emp.id,
        partner_id=emp.partner_id,
        partner_brand=partner.brand if partner else "",
        login=emp.login,
        full_name=emp.full_name,
        email=emp.email,
        phone=emp.phone,
        role=emp.role,
        is_active=emp.is_active,
        must_change_password=emp.must_change_password,
        last_login_at=emp.last_login_at,
    )


@router.post("/partner/change-password", response_model=OkResponse)
async def partner_change_password(
    payload: PartnerChangePasswordIn,
    emp: CurrentPartnerEmployee,
    db: DbSession,
) -> OkResponse:
    if not verify_password(payload.old_password, emp.password_hash):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Старый пароль неверен")
    emp.password_hash = hash_password(payload.new_password)
    emp.must_change_password = False
    await db.commit()
    return OkResponse(message="Пароль успешно изменён")


# ════════════ Клиент (Mini App / Сайт) ════════════
@router.post("/customer/otp/request", response_model=CustomerOtpRequestOut)
async def customer_otp_request(
    payload: CustomerOtpRequestIn, db: DbSession
) -> CustomerOtpRequestOut:
    code = await issue_otp(db, payload.phone, purpose="login")
    await db.commit()
    debug_code = code if settings.ENV in ("development", "test") else None
    return CustomerOtpRequestOut(sent=True, debug_code=debug_code)


@router.post("/customer/otp/verify", response_model=CustomerLoginOut)
async def customer_otp_verify(
    payload: CustomerOtpVerifyIn, db: DbSession
) -> CustomerLoginOut:
    ok = await verify_otp(db, payload.phone, payload.code)
    if not ok:
        await db.commit()
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Код неверен или истёк")

    res = await db.execute(select(Customer).where(Customer.phone == payload.phone))
    customer = res.scalar_one_or_none()
    is_new = customer is None
    if is_new:
        customer = Customer(phone=payload.phone)
        db.add(customer)
        await db.flush()

    customer.last_login_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(customer)

    return CustomerLoginOut(
        tokens=_issue_tokens(customer.id, "client"),
        user=CustomerMe.model_validate(customer),
        is_new=is_new,
    )


@router.post("/customer/click", response_model=CustomerLoginOut)
async def customer_click_auth(
    payload: CustomerClickAuthIn, db: DbSession
) -> CustomerLoginOut:
    """Авторизация через Click ID (внутри Mini App). В v1 — упрощённая, без HMAC-проверки от Click."""
    # ищем по click_user_id или по phone
    res = await db.execute(
        select(Customer).where(
            (Customer.click_user_id == payload.click_user_id) | (Customer.phone == payload.phone)
        )
    )
    customer = res.scalar_one_or_none()
    is_new = customer is None
    if is_new:
        customer = Customer(
            phone=payload.phone,
            click_user_id=payload.click_user_id,
            full_name=payload.full_name,
            email=payload.email,
        )
        db.add(customer)
        await db.flush()
    else:
        if not customer.click_user_id:
            customer.click_user_id = payload.click_user_id

    customer.last_login_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(customer)

    return CustomerLoginOut(
        tokens=_issue_tokens(customer.id, "client"),
        user=CustomerMe.model_validate(customer),
        is_new=is_new,
    )


@router.get("/customer/me", response_model=CustomerMe)
async def customer_me(customer: CurrentCustomer) -> CustomerMe:
    return CustomerMe.model_validate(customer)
