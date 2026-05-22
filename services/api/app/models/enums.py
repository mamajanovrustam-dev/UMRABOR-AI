"""Все enum'ы доменной модели UMRABOR. Текстовые значения совпадают с UI прототипов."""

from enum import StrEnum


class UmraborRole(StrEnum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"


class PartnerRole(StrEnum):
    ADMIN = "admin"
    OPERATOR = "operator"


class PartnerStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"
    PENDING = "pending"


class PackageStatus(StrEnum):
    DRAFT = "draft"
    MODERATION = "moderation"
    REWORK = "rework"
    PUBLISHED = "published"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class PackageType(StrEnum):
    PREMIUM = "premium"
    STANDARD = "standard"
    ECONOMY = "economy"


class BookingStatus(StrEnum):
    NEW = "new"           # Янги
    PROCESSING = "processing"  # Жараёнда
    KABUL = "kabul"       # Қабул (принято/подтверждено)
    COMPLETED = "completed"  # Тугалланди
    CANCELLED = "cancelled"  # Бекор


class BookingSource(StrEnum):
    CLICK = "click"       # Mini App
    MOBILE = "mobile"     # отдельное mobile-app (roadmap)
    WEB = "web"           # веб-сайт


class PaymentStatus(StrEnum):
    PENDING = "pending"
    SUCCESS = "success"
    REFUND = "refund"
    FAILED = "failed"


class PaymentChannel(StrEnum):
    CLICK = "click"
    PAYME = "payme"
    PAYNET = "paynet"
    CARD = "card"


class Gender(StrEnum):
    MALE = "M"
    FEMALE = "F"


class DocumentType(StrEnum):
    ZAGRAN = "zagran"     # Загранпасорт
    ID_PASS = "id_pass"   # ID-паспорт


class MahramRelation(StrEnum):
    HUSBAND = "husband"   # эри
    WIFE = "wife"
    FATHER = "father"     # ота
    MOTHER = "mother"     # она
    SON = "son"           # ўғли
    DAUGHTER = "daughter"
    BROTHER = "brother"   # ака
    SISTER = "sister"     # опа


class RoomType(StrEnum):
    """Тип комнаты — комбинация капасити (SGL/DBL/TRPL/QUAD) и пола (F/M/FM)."""
    SGL = "SGL"
    DBL_F = "DBL_F"
    DBL_M = "DBL_M"
    DBL_FM = "DBL_FM"
    TRPL_F = "TRPL_F"
    TRPL_M = "TRPL_M"
    TRPL_FM = "TRPL_FM"
    QUAD_F = "QUAD_F"
    QUAD_M = "QUAD_M"
    QUAD_FM = "QUAD_FM"
    QUAD_F3 = "QUAD_F3"   # 3+1, по умолчанию off
    QUAD_M3 = "QUAD_M3"   # 3+1, по умолчанию off


class City(StrEnum):
    MADINA = "madina"
    MAKKAH = "makkah"
    JEDDAH = "jeddah"
    OTHER = "other"


class HotelAmenity(StrEnum):
    WIFI = "wifi"
    AC = "ac"
    POOL = "pool"
    RESTAURANT = "restaurant"
    SHUTTLE = "shuttle"
    LIFT = "lift"
    SPA = "spa"
    LAUNDRY = "laundry"
    GYM = "gym"
    PARKING = "parking"
    CAFE = "cafe"
    SHOPS = "shops"


class ServiceCategory(StrEnum):
    DOCUMENTS = "documents"
    TRANSPORT = "transport"
    GUIDE = "guide"
    GIFT = "gift"
    OTHER = "other"


class GiftBrand(StrEnum):
    STANDARD = "standard"
    PREMIUM = "premium"
    LUX = "lux"


class DirectoryStatus(StrEnum):
    ACTIVE = "active"
    DRAFT = "draft"
    DISABLED = "disabled"


class ModerationDecision(StrEnum):
    APPROVED = "approved"
    REJECTED = "rejected"
    REWORK = "rework"


class NotificationChannel(StrEnum):
    PUSH = "push"
    SMS = "sms"
    EMAIL = "email"


class NotificationTrigger(StrEnum):
    NEW_BOOKING = "new_booking"
    BOOKING_ACCEPTED = "booking_accepted"
    BOOKING_REJECTED = "booking_rejected"
    SLA_WARNING = "sla_warning"
    NEW_MESSAGE = "new_message"
    INVENTORY_LOW = "inventory_low"
    INVENTORY_EMPTY = "inventory_empty"


class AuditAction(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    APPROVE = "approve"
    REJECT = "reject"
    REWORK = "rework"
    PUBLISH = "publish"
    WITHDRAW = "withdraw"
    SUSPEND = "suspend"
    REACTIVATE = "reactivate"
    PAYMENT = "payment"
    REFUND = "refund"


class ChatThreadType(StrEnum):
    CUSTOMER_PARTNER = "customer_partner"  # клиент ↔ оператор партнёра
    CUSTOMER_SUPPORT = "customer_support"  # клиент ↔ UMRABOR саппорт


class Locale(StrEnum):
    UZ_CYRL = "uz-Cyrl"
    UZ_LATN = "uz-Latn"
    RU = "ru"
    EN = "en"
