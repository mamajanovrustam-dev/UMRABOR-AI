"""ORM-модели UMRABOR. Импортируем всё для autodiscover Alembic."""

from app.models.audit import AuditLog, Notification
from app.models.auth import OtpCode, RefreshToken
from app.models.booking import (
    Booking,
    BookingEvent,
    BookingPilgrim,
    ChatMessage,
    ChatThread,
    Placement,
)
from app.models.customer import Customer, Pilgrim
from app.models.directory import (
    Airline,
    Gift,
    Hotel,
    InventoryType,
    MealType,
    PackageTypeDir,
    PartnerInventorySetting,
    RejectReason,
    Service,
    TransferType,
)
from app.models.package import (
    Departure,
    DepartureInventory,
    Package,
    PackageGift,
    PackageHotel,
    PackageModeration,
    PackageService,
)
from app.models.partner import Partner, PartnerEmployee, PartnerStatusHistory
from app.models.payment import Payment
from app.models.user_umrabor import UserUmrabor

__all__ = [
    "Airline",
    "AuditLog",
    "Booking",
    "BookingEvent",
    "BookingPilgrim",
    "ChatMessage",
    "ChatThread",
    "Customer",
    "Departure",
    "DepartureInventory",
    "Gift",
    "Hotel",
    "InventoryType",
    "MealType",
    "Notification",
    "OtpCode",
    "Package",
    "PackageGift",
    "PackageHotel",
    "PackageModeration",
    "PackageService",
    "PackageTypeDir",
    "Partner",
    "PartnerEmployee",
    "PartnerInventorySetting",
    "PartnerStatusHistory",
    "Payment",
    "Pilgrim",
    "Placement",
    "RefreshToken",
    "RejectReason",
    "Service",
    "TransferType",
    "UserUmrabor",
]
