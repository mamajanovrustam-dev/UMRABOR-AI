"""Endpoints генерации/скачивания ваучеров."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response

from app.api.deps import CurrentCustomer, CurrentPartnerEmployee, DbSession
from app.models import Booking
from app.services.voucher import generate_voucher_pdf

router = APIRouter()


async def _check_booking_access(db, booking_id: UUID, subject_id: UUID, kind: str) -> Booking:
    b = await db.get(Booking, booking_id)
    if b is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Заявка не найдена")
    if kind == "client" and b.customer_id != subject_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Нет доступа")
    if kind == "partner_employee":
        from app.models import PartnerEmployee
        emp = await db.get(PartnerEmployee, subject_id)
        if emp is None or b.partner_id != emp.partner_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Нет доступа")
    return b


@router.post("/customer/{booking_id}/generate", response_class=Response)
async def generate_voucher_as_customer(
    booking_id: UUID, customer: CurrentCustomer, db: DbSession
) -> Response:
    await _check_booking_access(db, booking_id, customer.id, "client")
    pdf, filename = await generate_voucher_pdf(db, booking_id)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/partner/{booking_id}/generate", response_class=Response)
async def generate_voucher_as_partner(
    booking_id: UUID, emp: CurrentPartnerEmployee, db: DbSession
) -> Response:
    await _check_booking_access(db, booking_id, emp.id, "partner_employee")
    pdf, filename = await generate_voucher_pdf(db, booking_id)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
