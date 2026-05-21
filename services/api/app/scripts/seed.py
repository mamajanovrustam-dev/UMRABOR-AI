"""Загрузка demo-данных UMRABOR на основе брифа.

Запуск: python -m app.scripts.seed
"""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, date, datetime, timedelta
from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models import (
    Airline,
    Booking,
    BookingEvent,
    BookingPilgrim,
    Customer,
    Departure,
    DepartureInventory,
    Gift,
    Hotel,
    InventoryType,
    MealType,
    Package,
    PackageGift,
    PackageHotel,
    PackageService,
    PackageTypeDir,
    Partner,
    PartnerEmployee,
    PartnerInventorySetting,
    PartnerStatusHistory,
    Payment,
    Pilgrim,
    Placement,
    RejectReason,
    Service,
    TransferType,
    UserUmrabor,
)
from app.models.enums import (
    BookingSource,
    BookingStatus,
    City,
    DocumentType,
    Gender,
    GiftBrand,
    MahramRelation,
    PackageStatus,
    PartnerRole,
    PartnerStatus,
    PaymentChannel,
    PaymentStatus,
    RoomType,
    ServiceCategory,
    UmraborRole,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("seed")

DEFAULT_PWD = "Demo-2026!"


async def truncate_all(db: AsyncSession) -> None:
    """Чистим в обратном порядке зависимостей (без TRUNCATE — медленнее, но универсально)."""
    log.info("Очистка существующих данных...")
    for model in [
        Payment,
        BookingEvent,
        BookingPilgrim,
        Placement,
        Booking,
        DepartureInventory,
        Departure,
        PackageHotel,
        PackageService,
        PackageGift,
        Package,
        PartnerInventorySetting,
        Pilgrim,
        Customer,
        PartnerEmployee,
        PartnerStatusHistory,
        Partner,
        UserUmrabor,
        Hotel,
        Airline,
        Service,
        Gift,
        MealType,
        PackageTypeDir,
        TransferType,
        RejectReason,
        InventoryType,
    ]:
        await db.execute(delete(model))
    await db.flush()


# ════════════ DIRECTORIES ════════════
async def seed_directories(db: AsyncSession) -> dict[str, dict]:
    log.info("Справочники...")

    # Авиакомпании
    airlines = {
        "HY": Airline(
            name="UZAIRWAYS", iata="HY", country="Узбекистан", base_iata="TAS", base_city="Ташкент",
            logo_color="#1E5BC6",
        ),
        "QR": Airline(
            name="Qatar Airways", iata="QR", country="Катар", base_iata="DOH", base_city="Доха",
            logo_color="#5C0F3C",
        ),
        "FZ": Airline(
            name="FlyDubai", iata="FZ", country="ОАЭ", base_iata="DXB", base_city="Дубай",
            logo_color="#0E2B65",
        ),
        "SV": Airline(
            name="Saudia", iata="SV", country="Саудовская Аравия", base_iata="JED", base_city="Жидда",
            logo_color="#1B7A35",
        ),
        "TK": Airline(
            name="Turkish Airlines", iata="TK", country="Турция", base_iata="IST",
            base_city="Стамбул", logo_color="#C8102E",
        ),
    }
    db.add_all(airlines.values())

    # Отели
    hotels_data = [
        ("Hayah Madinah", "hayah-madinah", City.MADINA, 5, 250, "м до Набавий",
         ["wifi", "ac", "restaurant", "lift", "parking", "cafe"]),
        ("Movenpick Madinah", "movenpick-madinah", City.MADINA, 5, 150, "м до Набавий",
         ["wifi", "ac", "restaurant", "lift", "parking", "cafe", "spa", "laundry"]),
        ("Dar Al-Iman", "dar-al-iman", City.MADINA, 4, 50, "м до Набавий",
         ["wifi", "ac", "restaurant", "lift"]),
        ("Pullman ZamZam Madinah", "pullman-zamzam-madinah", City.MADINA, 5, 100, "м до Набавий",
         ["wifi", "ac", "restaurant", "lift", "spa"]),
        ("Hilton Suites Makkah", "hilton-suites-makkah", City.MAKKAH, 5, 500, "м до Аль-Ҳарам",
         ["wifi", "ac", "restaurant", "lift", "parking"]),
        ("Ramada Al Qasr", "ramada-al-qasr", City.MAKKAH, 5, 800, "м до Аль-Ҳарам",
         ["wifi", "ac", "restaurant", "lift"]),
        ("Pullman ZamZam Makkah", "pullman-zamzam-makkah", City.MAKKAH, 5, 200, "м до Аль-Ҳарам",
         ["wifi", "ac", "restaurant", "lift", "spa", "shops"]),
        ("Anjum Hotel", "anjum-hotel", City.MAKKAH, 4, 200, "м до Аль-Ҳарам",
         ["wifi", "ac", "restaurant", "lift"]),
    ]
    hotels = {}
    for name, slug, city, stars, dist, dist_label, amenities in hotels_data:
        h = Hotel(
            name=name, slug=slug, city=city, stars=stars,
            distance_value=float(dist), distance_unit=dist_label.split(" ")[0],
            description=f"{name} — {stars}★, {dist} {dist_label}",
            amenities=amenities,
            photos=[f"https://images.pexels.com/photos/{1000 + i*100}/pexels-photo.jpeg"
                    for i in range(3)],
        )
        hotels[slug] = h
        db.add(h)

    # Услуги
    services_data = [
        ("🛂", "Виза", ServiceCategory.DOCUMENTS, "Саудия · 5 кун"),
        ("🚄", "Haramain поезд", ServiceCategory.TRANSPORT, "Мадина → Макка"),
        ("🚌", "Автобус", ServiceCategory.TRANSPORT, "Жидда ↔ Мадина"),
        ("🕌", "Гид-имом", ServiceCategory.GUIDE, "UZ-тил"),
        ("🛡", "Страховка", ServiceCategory.DOCUMENTS, "Все включено"),
        ("💧", "Зам-зам", ServiceCategory.GIFT, "5 л"),
        ("🎒", "Сумка", ServiceCategory.GIFT, "Brand-set"),
        ("📱", "Мобильный", ServiceCategory.OTHER, "10 GB"),
        ("📜", "Сертификат", ServiceCategory.DOCUMENTS, "После"),
    ]
    services = {}
    for icon, name, cat, desc in services_data:
        s = Service(icon=icon, name=name, category=cat, description=desc)
        services[name] = s
        db.add(s)

    # Подарки
    gifts_data = [
        ("🎒", "Эко-сумка", GiftBrand.STANDARD, 120_000),
        ("🎧", "Наушники", GiftBrand.PREMIUM, 250_000),
        ("🛏", "Плед", GiftBrand.STANDARD, 90_000),
        ("📿", "Чётки тасбех", GiftBrand.PREMIUM, 80_000),
        ("🕋", "Сувенир Каабы", GiftBrand.STANDARD, 45_000),
        ("📖", "Дуа китоби", GiftBrand.STANDARD, 60_000),
    ]
    gifts = {}
    for icon, name, brand, cost in gifts_data:
        g = Gift(icon=icon, name=name, brand=brand, cost_uzs=cost)
        gifts[name] = g
        db.add(g)

    # Типы питания
    meal_types = {}
    for name in ["Шведский стол", "Комплексное питание", "Индивидуальное меню",
                 "Ресторанное питание", "Другое"]:
        mt = MealType(name=name)
        meal_types[name] = mt
        db.add(mt)

    # Типы пакета
    package_types = {}
    for name in ["Премиум", "Стандарт", "Эконом"]:
        pt = PackageTypeDir(name=name)
        package_types[name] = pt
        db.add(pt)

    # Типы трансфера
    transfers = {}
    for icon, name in [("🚌", "Автобус"), ("✈", "Самолёт"),
                        ("🚄", "Скоростной поезд"), ("🚐", "Миниавтобус")]:
        t = TransferType(icon=icon, name=name)
        transfers[name] = t
        db.add(t)

    # Причины отказа
    rejects = {}
    for name, desc in [
        ("Нет возможности разместить",
         "Кончились места нужной комнаты или пол не совпадает"),
        ("Нет документов", "Не загружен паспорт или документ просрочен"),
        ("Информация неверна",
         "Серия/номер паспорта не совпадает с фото или ошибка в ФИО"),
        ("Другое", "Свободная причина"),
    ]:
        r = RejectReason(name=name, description=desc)
        rejects[name] = r
        db.add(r)

    # Типы размещения
    inv_specs = [
        ("SGL", "Одноместный", 1, None, True, 0),
        ("DBL_F", "Двухместный, женщины", 2, "F", True, 10),
        ("DBL_M", "Двухместный, мужчины", 2, "M", True, 11),
        ("DBL_FM", "Двухместный, семейный", 2, "FM", True, 12),
        ("TRPL_F", "Трёхместный, женщины", 3, "F", True, 20),
        ("TRPL_M", "Трёхместный, мужчины", 3, "M", True, 21),
        ("TRPL_FM", "Трёхместный, семейный", 3, "FM", True, 22),
        ("QUAD_F", "4-местный, женщины", 4, "F", True, 30),
        ("QUAD_M", "4-местный, мужчины", 4, "M", True, 31),
        ("QUAD_FM", "4-местный, семейный", 4, "FM", True, 32),
        ("QUAD_F3", "4-местный, женщины (3+1)", 4, "F", False, 33),
        ("QUAD_M3", "4-местный, мужчины (3+1)", 4, "M", False, 34),
    ]
    inventory_types = {}
    for code, label, cap, gender, enabled, sort_o in inv_specs:
        it = InventoryType(
            code=RoomType(code),
            label=label,
            capacity=cap,
            gender_constraint=gender,
            is_globally_enabled=enabled,
            sort_order=sort_o,
        )
        inventory_types[code] = it
        db.add(it)

    await db.flush()
    return {
        "airlines": airlines,
        "hotels": hotels,
        "services": services,
        "gifts": gifts,
        "meal_types": meal_types,
        "package_types": package_types,
        "transfers": transfers,
        "rejects": rejects,
        "inventory_types": inventory_types,
    }


# ════════════ UMRABOR USERS ════════════
async def seed_umrabor_users(db: AsyncSession) -> dict[str, UserUmrabor]:
    log.info("Сотрудники UMRABOR...")
    pwd = hash_password(DEFAULT_PWD)
    users_spec = [
        ("yulia.m", "Юлия Маҳмудова", UmraborRole.SUPER_ADMIN, True),
        ("anvar.q", "Анвар Қурбонов", UmraborRole.ADMIN, True),
        ("dilfuza.t", "Дилфуза Турсунова", UmraborRole.ADMIN, True),
        ("sherali.a", "Шерали Алиев", UmraborRole.ADMIN, True),
        ("malika.b", "Малика Бакаева", UmraborRole.ADMIN, False),
    ]
    users = {}
    for login, name, role, active in users_spec:
        u = UserUmrabor(
            login=login,
            full_name=name,
            password_hash=pwd,
            role=role,
            is_active=active,
            email=f"{login}@umrabor.uz",
        )
        users[login] = u
        db.add(u)
    await db.flush()
    return users


# ════════════ PARTNERS ════════════
async def seed_partners(db: AsyncSession, super_user: UserUmrabor) -> dict[str, Partner]:
    log.info("Партнёры...")
    pwd = hash_password(DEFAULT_PWD)

    partners_spec = [
        {
            "legal_name": "ООО «Ramaz Travel»",
            "brand": "Ramaz Travel",
            "slug": "ramaz-travel",
            "city": "Ташкент",
            "founded_year": 2023,
            "license_no": "002",
            "license_issued_at": date(2023, 3, 1),
            "license_until": date(2027, 3, 1),
            "inn": "305432109",
            "oked": "79.11",
            "bank_account": "20208000082450312001",
            "bank_name": "АКБ Узпромстройбанк",
            "bank_mfo": "00440",
            "vat_code": "3000123456",
            "legal_address": "Ташкент, ул. Амира Темура 108",
            "actual_address": "Ташкент, ул. Амира Темура 108",
            "contact_full_name": "Турсунов Жасур Мухаммадович",
            "contact_position": "Директор",
            "contact_phone": "+998901234567",
            "contact_email": "info@ramaztravel.uz",
        },
        {
            "legal_name": "ООО «Safar Tours»",
            "brand": "Safar Tours",
            "slug": "safar-tours",
            "city": "Самарканд",
            "founded_year": 2024,
            "license_no": "045",
            "license_issued_at": date(2024, 1, 15),
            "license_until": date(2028, 1, 15),
            "inn": "309876543",
            "contact_full_name": "Каримов Бахром",
            "contact_phone": "+998935550123",
            "contact_email": "info@safartours.uz",
        },
        {
            "legal_name": "ООО «Barakah VIP»",
            "brand": "Barakah VIP",
            "slug": "barakah-vip",
            "city": "Ташкент",
            "founded_year": 2024,
            "license_no": "067",
            "license_issued_at": date(2024, 5, 1),
            "license_until": date(2028, 5, 1),
            "inn": "304567812",
            "contact_phone": "+998901119988",
            "contact_email": "info@barakah-vip.uz",
        },
        {
            "legal_name": "ООО «Nur Travel»",
            "brand": "Nur Travel",
            "slug": "nur-travel",
            "city": "Бухара",
            "founded_year": 2023,
            "license_no": "023",
            "license_issued_at": date(2022, 6, 18),
            "license_until": date(2026, 6, 18),
            "inn": "302345678",
            "contact_phone": "+998933334411",
            "contact_email": "info@nurtravel.uz",
        },
        {
            "legal_name": "ООО «Hajj.uz»",
            "brand": "Hajj.uz",
            "slug": "hajj-uz",
            "city": "Андижан",
            "founded_year": 2024,
            "license_no": "089",
            "license_issued_at": date(2024, 2, 12),
            "license_until": date(2026, 6, 12),
            "inn": "307890123",
            "contact_phone": "+998999998877",
            "contact_email": "info@hajj.uz",
        },
        {
            "legal_name": "ООО «Umra Premium»",
            "brand": "Umra Premium",
            "slug": "umra-premium",
            "city": "Ташкент",
            "founded_year": 2026,
            "license_no": "102",
            "license_issued_at": date(2026, 5, 15),
            "license_until": date(2030, 1, 1),
            "inn": "308901234",
            "contact_phone": "+998901112233",
            "contact_email": "info@umrapremium.uz",
        },
    ]

    partners = {}
    for spec in partners_spec:
        p = Partner(status=PartnerStatus.ACTIVE, **spec)
        partners[spec["slug"]] = p
        db.add(p)
    await db.flush()

    # История статусов — для всех «Активирован»
    for p in partners.values():
        h = PartnerStatusHistory(
            partner_id=p.id,
            status=PartnerStatus.ACTIVE,
            reason="Активация после первичной модерации",
            changed_by_user_id=super_user.id,
        )
        db.add(h)
    await db.flush()

    # Сотрудники партнёров
    employees_spec = {
        "ramaz-travel": [
            ("ibrahim.r", "Иброҳим Расулов", PartnerRole.ADMIN, True),
            ("dilfuza.t-rt", "Дилфуза Турсунова", PartnerRole.OPERATOR, True),
            ("sherali.a-rt", "Шерали Алиев", PartnerRole.OPERATOR, True),
            ("malika.y", "Малика Юлдашева", PartnerRole.OPERATOR, True),
            ("jasur.k", "Жасур Каримов", PartnerRole.OPERATOR, False),
        ],
        "safar-tours": [
            ("safar.admin", "Бахром Каримов", PartnerRole.ADMIN, True),
            ("safar.op1", "Шахзод Усмонов", PartnerRole.OPERATOR, True),
        ],
        "barakah-vip": [
            ("barakah.admin", "Алишер Шарипов", PartnerRole.ADMIN, True),
        ],
        "nur-travel": [
            ("nur.admin", "Фарход Назиров", PartnerRole.ADMIN, True),
        ],
        "hajj-uz": [
            ("hajj.admin", "Бекзод Юлдашев", PartnerRole.ADMIN, True),
        ],
        "umra-premium": [
            ("umra.admin", "Зариф Холиков", PartnerRole.ADMIN, True),
        ],
    }
    for pslug, emps in employees_spec.items():
        partner = partners[pslug]
        for login, name, role, active in emps:
            emp = PartnerEmployee(
                partner_id=partner.id,
                login=login,
                full_name=name,
                password_hash=pwd,
                must_change_password=False,
                role=role,
                is_active=active,
                phone=f"+99890{abs(hash(login)) % 10_000_000:07d}",
                email=f"{login.replace('.', '_')}@{pslug.replace('-', '')}.uz",
            )
            db.add(emp)
    await db.flush()
    return partners


# ════════════ CUSTOMER + PILGRIMS ════════════
async def seed_customer(db: AsyncSession) -> tuple[Customer, list[Pilgrim]]:
    log.info("Демо-клиент и паломники...")
    c = Customer(
        phone="+998901234321",
        email="sardor@example.com",
        full_name="Раҳимов Сардор",
        first_name="Сардор",
        last_name="Раҳимов",
        gender=Gender.MALE,
        birth_date=date(1985, 6, 15),
        click_user_id="CLK-7842919",
    )
    db.add(c)
    await db.flush()

    pilgrims_data = [
        # Сардор — мужчина, махрам для Мадины
        dict(
            last_name="Раҳимов", first_name="Сардор", full_name="Раҳимов Сардор",
            gender=Gender.MALE, birth_date=date(1985, 6, 15),
            document_type=DocumentType.ZAGRAN,
            document_series_number="AA1234567",
            document_valid_until=date(2030, 12, 31),
        ),
        # Жасур — мужчина, ID-паспорт
        dict(
            last_name="Раҳимов", first_name="Жасур", full_name="Раҳимов Жасур",
            gender=Gender.MALE, birth_date=date(1990, 9, 22),
            document_type=DocumentType.ID_PASS,
            document_series_number="BB7654321",
            document_valid_until=date(2031, 3, 31),
        ),
        # Мадина — женщина, махрам = Сардор
        dict(
            last_name="Раҳимова", first_name="Мадина", full_name="Раҳимова Мадина",
            gender=Gender.FEMALE, birth_date=date(1992, 4, 3),
            document_type=DocumentType.ZAGRAN,
            document_series_number="CC9876543",
            document_valid_until=date(2028, 11, 30),
        ),
    ]
    pilgrims = []
    for pd in pilgrims_data:
        p = Pilgrim(customer_id=c.id, **pd)
        pilgrims.append(p)
        db.add(p)
    await db.flush()

    # Махрам-связь: Мадина → Сардор (эри)
    pilgrims[2].mahram_pilgrim_id = pilgrims[0].id
    pilgrims[2].mahram_relation = MahramRelation.HUSBAND
    await db.flush()

    return c, pilgrims


# ════════════ PACKAGES ════════════
async def seed_packages(
    db: AsyncSession, partners: dict[str, Partner], dirs: dict
) -> dict[str, Package]:
    log.info("Пакеты с вылетами и инвентарём...")

    def make_package(
        *,
        partner_slug: str,
        name: str,
        slug: str,
        ptype: str,
        airline: str,
        meal: str,
        transfer: str,
        duration: int,
        route: list[str],
        prices: tuple[int | None, int, int, int],
        hotels_cfg: list[tuple[str, int]],  # (hotel_slug, nights)
        services_list: list[str],
        gifts_list: list[str],
        departures: list[dict],
        status: PackageStatus,
        description: str | None = None,
    ) -> Package:
        partner = partners[partner_slug]
        p = Package(
            partner_id=partner.id,
            name=name,
            slug=slug,
            package_type_id=dirs["package_types"][ptype].id,
            airline_id=dirs["airlines"][airline].id,
            meal_type_id=dirs["meal_types"][meal].id,
            transfer_type_id=dirs["transfers"][transfer].id,
            duration_days=duration,
            route=route,
            description=description or f"{name} — {duration} кун, {' → '.join(route)}",
            photos=[f"https://images.pexels.com/photos/{2675268 + i}/pexels-photo.jpeg"
                    for i in range(4)],
            price_sgl=prices[0],
            price_dbl=prices[1],
            price_trpl=prices[2],
            price_quad=prices[3],
            status=status,
            submitted_at=datetime.now(UTC) - timedelta(days=5),
            moderated_at=(datetime.now(UTC) - timedelta(days=3))
            if status == PackageStatus.PUBLISHED
            else None,
        )
        db.add(p)
        return p

    pkgs: dict[str, Package] = {}

    base_dep_2026 = date(2026, 6, 22)

    def std_inventory(dep_id, capacity=45, breakdown=None):
        """Создаёт DepartureInventory по типам."""
        default = breakdown or {
            RoomType.DBL_FM: capacity // 3,
            RoomType.TRPL_FM: capacity // 3,
            RoomType.QUAD_FM: capacity - 2 * (capacity // 3),
        }
        return [
            DepartureInventory(departure_id=dep_id, room_type=rt, capacity=cap, sold=0)
            for rt, cap in default.items()
        ]

    # 1. Премиум Баҳор — Ramaz Travel, опубликовано
    p1 = make_package(
        partner_slug="ramaz-travel",
        name="Премиум Баҳор",
        slug="premium-bahor",
        ptype="Премиум",
        airline="QR",
        meal="Шведский стол",
        transfer="Самолёт",
        duration=12,
        route=["Жидда", "Мадина", "Макка", "Жидда"],
        prices=(26_800_000, 23_400_000, 19_500_000, 17_200_000),
        hotels_cfg=[("movenpick-madinah", 4), ("hilton-suites-makkah", 7)],
        services_list=["Виза", "Гид-имом", "Страховка", "Зам-зам", "Сумка", "Сертификат"],
        gifts_list=["Эко-сумка", "Наушники", "Чётки тасбех"],
        departures=[],
        status=PackageStatus.PUBLISHED,
        description="Премиум-пакет на 12 кун с проживанием в люкс-отелях Movenpick и Hilton. "
                    "Включены трансферы Haramain экспрессом, виза и опытный гид-имом.",
    )
    pkgs["premium-bahor"] = p1

    # 2. Премиум 3 шаҳар — Ramaz Travel
    p2 = make_package(
        partner_slug="ramaz-travel",
        name="Премиум 3 шаҳар",
        slug="premium-3-shahar",
        ptype="Премиум",
        airline="QR",
        meal="Шведский стол",
        transfer="Скоростной поезд",
        duration=12,
        route=["Жидда", "Мадина", "Макка", "Жидда"],
        prices=(26_800_000, 23_400_000, 19_500_000, 17_200_000),
        hotels_cfg=[("movenpick-madinah", 4), ("hilton-suites-makkah", 7)],
        services_list=["Виза", "Гид-имом", "Страховка", "Зам-зам", "Сумка", "Сертификат"],
        gifts_list=["Эко-сумка", "Наушники"],
        departures=[],
        status=PackageStatus.PUBLISHED,
    )
    pkgs["premium-3-shahar"] = p2

    # 3. Рамазон Люкс 2026 — Ramaz Travel
    p3 = make_package(
        partner_slug="ramaz-travel",
        name="Рамазон Люкс 2026",
        slug="ramazon-lux-2026",
        ptype="Премиум",
        airline="HY",
        meal="Шведский стол",
        transfer="Скоростной поезд",
        duration=10,
        route=["Мадина", "Макка"],
        prices=(31_500_000, 26_800_000, 22_300_000, 19_500_000),
        hotels_cfg=[("movenpick-madinah", 3), ("pullman-zamzam-makkah", 7)],
        services_list=["Виза", "Гид-имом", "Страховка", "Зам-зам", "Сумка"],
        gifts_list=["Эко-сумка", "Чётки тасбех"],
        departures=[],
        status=PackageStatus.PUBLISHED,
    )
    pkgs["ramazon-lux-2026"] = p3

    # 4. Эконом пакет — Ramaz Travel
    p4 = make_package(
        partner_slug="ramaz-travel",
        name="Эконом пакет",
        slug="econom",
        ptype="Эконом",
        airline="FZ",
        meal="Комплексное питание",
        transfer="Автобус",
        duration=12,
        route=["Мадина", "Макка"],
        prices=(None, 16_200_000, 13_500_000, 11_800_000),
        hotels_cfg=[("dar-al-iman", 3), ("ramada-al-qasr", 9)],
        services_list=["Виза", "Автобус", "Гид-имом", "Страховка"],
        gifts_list=["Эко-сумка", "Дуа китоби"],
        departures=[],
        status=PackageStatus.PUBLISHED,
    )
    pkgs["econom"] = p4

    # 5. Стандарт пакет — Safar Tours
    p5 = make_package(
        partner_slug="safar-tours",
        name="Стандарт пакет",
        slug="standard",
        ptype="Стандарт",
        airline="HY",
        meal="Комплексное питание",
        transfer="Скоростной поезд",
        duration=12,
        route=["Жидда", "Мадина", "Макка", "Жидда"],
        prices=(None, 19_900_000, 16_800_000, 14_500_000),
        hotels_cfg=[("hayah-madinah", 3), ("anjum-hotel", 8)],
        services_list=["Виза", "Гид-имом", "Страховка", "Зам-зам"],
        gifts_list=["Эко-сумка", "Чётки тасбех"],
        departures=[],
        status=PackageStatus.PUBLISHED,
    )
    pkgs["standard"] = p5

    # 6. Премиум Баҳор VIP — Barakah VIP
    p6 = make_package(
        partner_slug="barakah-vip",
        name="Премиум Баҳор VIP",
        slug="premium-bahor-vip",
        ptype="Премиум",
        airline="SV",
        meal="Ресторанное питание",
        transfer="Самолёт",
        duration=14,
        route=["Жидда", "Мадина", "Макка", "Жидда"],
        prices=(36_400_000, 31_700_000, 26_300_000, 22_800_000),
        hotels_cfg=[("movenpick-madinah", 4), ("pullman-zamzam-makkah", 9)],
        services_list=["Виза", "Гид-имом", "Страховка", "Зам-зам", "Сумка", "Сертификат", "Мобильный"],
        gifts_list=["Наушники", "Сувенир Каабы", "Плед"],
        departures=[],
        status=PackageStatus.PUBLISHED,
    )
    pkgs["premium-bahor-vip"] = p6

    # 7. Хадж 2026 Премиум — Barakah VIP, на доработке
    p7 = make_package(
        partner_slug="barakah-vip",
        name="Хадж 2026 Премиум",
        slug="hajj-2026-premium",
        ptype="Премиум",
        airline="SV",
        meal="Ресторанное питание",
        transfer="Самолёт",
        duration=21,
        route=["Жидда", "Мадина", "Макка", "Жидда"],
        prices=(85_000_000, 78_000_000, 72_000_000, None),  # без QUAD
        hotels_cfg=[("movenpick-madinah", 8), ("pullman-zamzam-makkah", 12)],
        services_list=["Виза", "Гид-имом", "Страховка"],
        gifts_list=["Наушники"],
        departures=[],
        status=PackageStatus.REWORK,
    )
    pkgs["hajj-2026-premium"] = p7

    # 8. Бухара Умра — Nur Travel
    p8 = make_package(
        partner_slug="nur-travel",
        name="Бухара Умра",
        slug="bukhara-umra",
        ptype="Стандарт",
        airline="HY",
        meal="Комплексное питание",
        transfer="Автобус",
        duration=14,
        route=["Жидда", "Мадина", "Макка", "Жидда"],
        prices=(None, 18_000_000, 15_500_000, 13_200_000),
        hotels_cfg=[("hayah-madinah", 5), ("ramada-al-qasr", 8)],
        services_list=["Виза", "Гид-имом", "Страховка"],
        gifts_list=["Дуа китоби"],
        departures=[],
        status=PackageStatus.PUBLISHED,
    )
    pkgs["bukhara-umra"] = p8

    # 9. Лайт Умра 2025 — Nur Travel, снят с продажи
    p9 = make_package(
        partner_slug="nur-travel",
        name="Лайт Умра 2025",
        slug="light-umra-2025",
        ptype="Эконом",
        airline="FZ",
        meal="Комплексное питание",
        transfer="Автобус",
        duration=7,
        route=["Мадина", "Макка"],
        prices=(None, 12_000_000, 10_500_000, 9_500_000),
        hotels_cfg=[("dar-al-iman", 2), ("ramada-al-qasr", 5)],
        services_list=["Виза", "Гид-имом"],
        gifts_list=["Эко-сумка"],
        departures=[],
        status=PackageStatus.WITHDRAWN,
    )
    pkgs["light-umra-2025"] = p9

    # 10. Умра Эконом 5 дней — Hajj.uz, отклонён
    p10 = make_package(
        partner_slug="hajj-uz",
        name="Умра Эконом 5 дней",
        slug="umra-econom-5-days",
        ptype="Эконом",
        airline="FZ",
        meal="Комплексное питание",
        transfer="Автобус",
        duration=5,
        route=["Мадина", "Макка"],
        prices=(None, 11_000_000, 9_500_000, 8_500_000),
        hotels_cfg=[("dar-al-iman", 1), ("ramada-al-qasr", 4)],
        services_list=["Виза"],
        gifts_list=[],
        departures=[],
        status=PackageStatus.REJECTED,
    )
    pkgs["umra-econom-5-days"] = p10

    # 11. Премиум Баҳор 2026 — Ramaz Travel, на модерации
    p11 = make_package(
        partner_slug="ramaz-travel",
        name="Премиум Баҳор 2026",
        slug="premium-bahor-2026",
        ptype="Премиум",
        airline="QR",
        meal="Шведский стол",
        transfer="Самолёт",
        duration=12,
        route=["Жидда", "Мадина", "Макка", "Жидда"],
        prices=(26_800_000, 24_000_000, 20_000_000, 17_500_000),
        hotels_cfg=[("movenpick-madinah", 4), ("hilton-suites-makkah", 7)],
        services_list=["Виза", "Гид-имом", "Страховка", "Зам-зам"],
        gifts_list=["Эко-сумка"],
        departures=[],
        status=PackageStatus.MODERATION,
    )
    pkgs["premium-bahor-2026"] = p11

    await db.flush()

    # Привязываем отели/услуги/подарки
    hotel_specs = {
        "premium-bahor": [("movenpick-madinah", 4), ("hilton-suites-makkah", 7)],
        "premium-3-shahar": [("movenpick-madinah", 4), ("hilton-suites-makkah", 7)],
        "ramazon-lux-2026": [("movenpick-madinah", 3), ("pullman-zamzam-makkah", 7)],
        "econom": [("dar-al-iman", 3), ("ramada-al-qasr", 9)],
        "standard": [("hayah-madinah", 3), ("anjum-hotel", 8)],
        "premium-bahor-vip": [("movenpick-madinah", 4), ("pullman-zamzam-makkah", 9)],
        "hajj-2026-premium": [("movenpick-madinah", 8), ("pullman-zamzam-makkah", 12)],
        "bukhara-umra": [("hayah-madinah", 5), ("ramada-al-qasr", 8)],
        "light-umra-2025": [("dar-al-iman", 2), ("ramada-al-qasr", 5)],
        "umra-econom-5-days": [("dar-al-iman", 1), ("ramada-al-qasr", 4)],
        "premium-bahor-2026": [("movenpick-madinah", 4), ("hilton-suites-makkah", 7)],
    }
    service_specs = {
        "premium-bahor": ["Виза", "Гид-имом", "Страховка", "Зам-зам", "Сумка", "Сертификат"],
        "premium-3-shahar": ["Виза", "Гид-имом", "Страховка", "Зам-зам", "Сумка", "Сертификат"],
        "ramazon-lux-2026": ["Виза", "Гид-имом", "Страховка", "Зам-зам", "Сумка"],
        "econom": ["Виза", "Автобус", "Гид-имом", "Страховка"],
        "standard": ["Виза", "Гид-имом", "Страховка", "Зам-зам"],
        "premium-bahor-vip": ["Виза", "Гид-имом", "Страховка", "Зам-зам", "Сумка", "Сертификат", "Мобильный"],
        "hajj-2026-premium": ["Виза", "Гид-имом", "Страховка"],
        "bukhara-umra": ["Виза", "Гид-имом", "Страховка"],
        "light-umra-2025": ["Виза", "Гид-имом"],
        "umra-econom-5-days": ["Виза"],
        "premium-bahor-2026": ["Виза", "Гид-имом", "Страховка", "Зам-зам"],
    }
    gift_specs = {
        "premium-bahor": ["Эко-сумка", "Наушники", "Чётки тасбех"],
        "premium-3-shahar": ["Эко-сумка", "Наушники"],
        "ramazon-lux-2026": ["Эко-сумка", "Чётки тасбех"],
        "econom": ["Эко-сумка", "Дуа китоби"],
        "standard": ["Эко-сумка", "Чётки тасбех"],
        "premium-bahor-vip": ["Наушники", "Сувенир Каабы", "Плед"],
        "hajj-2026-premium": ["Наушники"],
        "bukhara-umra": ["Дуа китоби"],
        "light-umra-2025": ["Эко-сумка"],
        "umra-econom-5-days": [],
        "premium-bahor-2026": ["Эко-сумка"],
    }

    for slug, hotels_list in hotel_specs.items():
        for idx, (hslug, nights) in enumerate(hotels_list):
            db.add(PackageHotel(
                package_id=pkgs[slug].id,
                hotel_id=dirs["hotels"][hslug].id,
                nights=nights,
                sort_order=idx,
            ))
    for slug, slist in service_specs.items():
        for sname in slist:
            db.add(PackageService(
                package_id=pkgs[slug].id,
                service_id=dirs["services"][sname].id,
            ))
    for slug, glist in gift_specs.items():
        for gname in glist:
            db.add(PackageGift(
                package_id=pkgs[slug].id,
                gift_id=dirs["gifts"][gname].id,
            ))
    await db.flush()

    # Создаём вылеты для опубликованных пакетов
    def add_departures(pkg: Package, dates: list[date], capacities_per_room: dict[RoomType, int]):
        for d_out in dates:
            d_in = d_out + timedelta(days=pkg.duration_days - 1)
            dep = Departure(
                package_id=pkg.id,
                date_out=d_out,
                date_in=d_in,
                flight_out="QR-2113",
                flight_in="QR-2114",
                aircraft="Boeing 787-9",
                baggage="30 кг + 7 кг",
                capacity_total=sum(capacities_per_room.values()),
            )
            db.add(dep)
            db.flush  # type: ignore[func-returns-value]
        return None

    # Премиум 3 шаҳар — 4 вылета, начиная с 10.10.2026
    for offset_weeks in (0, 1, 2, 3):
        d_out = date(2026, 10, 10) + timedelta(weeks=offset_weeks)
        dep = Departure(
            package_id=pkgs["premium-3-shahar"].id,
            date_out=d_out,
            date_in=d_out + timedelta(days=11),
            flight_out="QR-2113",
            flight_in="QR-2114",
            aircraft="Boeing 787-9",
            baggage="30 кг + 7 кг",
            capacity_total=30,
            sold_total=0,
        )
        db.add(dep)
        await db.flush()
        db.add_all([
            DepartureInventory(departure_id=dep.id, room_type=RoomType.SGL, capacity=4),
            DepartureInventory(departure_id=dep.id, room_type=RoomType.DBL_FM, capacity=10),
            DepartureInventory(departure_id=dep.id, room_type=RoomType.TRPL_FM, capacity=9),
            DepartureInventory(departure_id=dep.id, room_type=RoomType.QUAD_FM, capacity=7),
        ])

    # Премиум Баҳор — 4 вылета
    for offset_weeks in (0, 1, 2, 3):
        d_out = base_dep_2026 + timedelta(weeks=offset_weeks)
        dep = Departure(
            package_id=pkgs["premium-bahor"].id,
            date_out=d_out,
            date_in=d_out + timedelta(days=11),
            flight_out="QR-2113",
            flight_in="QR-2114",
            aircraft="Boeing 787-9",
            baggage="30 кг + 7 кг",
            capacity_total=45,
        )
        db.add(dep)
        await db.flush()
        db.add_all([
            DepartureInventory(departure_id=dep.id, room_type=RoomType.SGL, capacity=5),
            DepartureInventory(departure_id=dep.id, room_type=RoomType.DBL_FM, capacity=15),
            DepartureInventory(departure_id=dep.id, room_type=RoomType.TRPL_FM, capacity=15),
            DepartureInventory(departure_id=dep.id, room_type=RoomType.QUAD_FM, capacity=10),
        ])

    # Эконом пакет — 5 вылетов
    for offset_weeks in range(5):
        d_out = date(2026, 9, 15) + timedelta(weeks=offset_weeks)
        dep = Departure(
            package_id=pkgs["econom"].id,
            date_out=d_out,
            date_in=d_out + timedelta(days=11),
            flight_out="FZ-1815",
            flight_in="FZ-1816",
            aircraft="Boeing 737-800",
            baggage="20 кг + 7 кг",
            capacity_total=60,
        )
        db.add(dep)
        await db.flush()
        db.add_all([
            DepartureInventory(departure_id=dep.id, room_type=RoomType.DBL_F, capacity=10),
            DepartureInventory(departure_id=dep.id, room_type=RoomType.DBL_M, capacity=10),
            DepartureInventory(departure_id=dep.id, room_type=RoomType.DBL_FM, capacity=10),
            DepartureInventory(departure_id=dep.id, room_type=RoomType.TRPL_FM, capacity=15),
            DepartureInventory(departure_id=dep.id, room_type=RoomType.QUAD_FM, capacity=15),
        ])

    # Стандарт пакет — 4 вылета (Safar Tours)
    for offset_weeks in range(4):
        d_out = date(2026, 11, 11) + timedelta(weeks=offset_weeks)
        dep = Departure(
            package_id=pkgs["standard"].id,
            date_out=d_out,
            date_in=d_out + timedelta(days=11),
            flight_out="HY-541",
            flight_in="HY-542",
            aircraft="Boeing 787-8",
            baggage="25 кг + 7 кг",
            capacity_total=40,
        )
        db.add(dep)
        await db.flush()
        db.add_all([
            DepartureInventory(departure_id=dep.id, room_type=RoomType.DBL_FM, capacity=10),
            DepartureInventory(departure_id=dep.id, room_type=RoomType.TRPL_FM, capacity=15),
            DepartureInventory(departure_id=dep.id, room_type=RoomType.QUAD_FM, capacity=15),
        ])

    # Рамазон Люкс 2026 — 3 вылета
    for offset_weeks in range(3):
        d_out = date(2026, 6, 22) + timedelta(weeks=offset_weeks)
        dep = Departure(
            package_id=pkgs["ramazon-lux-2026"].id,
            date_out=d_out,
            date_in=d_out + timedelta(days=9),
            flight_out="HY-545",
            flight_in="HY-546",
            aircraft="Boeing 787-8",
            baggage="30 кг + 7 кг",
            capacity_total=50,
        )
        db.add(dep)
        await db.flush()
        db.add_all([
            DepartureInventory(departure_id=dep.id, room_type=RoomType.SGL, capacity=5),
            DepartureInventory(departure_id=dep.id, room_type=RoomType.DBL_FM, capacity=15),
            DepartureInventory(departure_id=dep.id, room_type=RoomType.TRPL_FM, capacity=15),
            DepartureInventory(departure_id=dep.id, room_type=RoomType.QUAD_FM, capacity=15),
        ])

    # Премиум Баҳор VIP (Barakah) — 2 вылета
    for offset_weeks in range(2):
        d_out = date(2026, 3, 18) + timedelta(weeks=offset_weeks * 2)
        dep = Departure(
            package_id=pkgs["premium-bahor-vip"].id,
            date_out=d_out,
            date_in=d_out + timedelta(days=13),
            flight_out="SV-563",
            flight_in="SV-564",
            aircraft="Boeing 777-300",
            baggage="35 кг + 10 кг",
            capacity_total=30,
        )
        db.add(dep)
        await db.flush()
        db.add_all([
            DepartureInventory(departure_id=dep.id, room_type=RoomType.SGL, capacity=5),
            DepartureInventory(departure_id=dep.id, room_type=RoomType.DBL_FM, capacity=10),
            DepartureInventory(departure_id=dep.id, room_type=RoomType.TRPL_FM, capacity=15),
        ])

    # Бухара Умра
    for offset_weeks in range(2):
        d_out = date(2026, 8, 5) + timedelta(weeks=offset_weeks * 2)
        dep = Departure(
            package_id=pkgs["bukhara-umra"].id,
            date_out=d_out,
            date_in=d_out + timedelta(days=13),
            flight_out="HY-547",
            flight_in="HY-548",
            aircraft="Airbus A320",
            baggage="23 кг + 7 кг",
            capacity_total=30,
        )
        db.add(dep)
        await db.flush()
        db.add_all([
            DepartureInventory(departure_id=dep.id, room_type=RoomType.DBL_F, capacity=10),
            DepartureInventory(departure_id=dep.id, room_type=RoomType.DBL_FM, capacity=10),
            DepartureInventory(departure_id=dep.id, room_type=RoomType.QUAD_FM, capacity=10),
        ])

    await db.flush()
    return pkgs


# ════════════ BOOKINGS & PAYMENTS ════════════
async def seed_bookings(
    db: AsyncSession,
    customer: Customer,
    pilgrims: list[Pilgrim],
    partners: dict[str, Partner],
    pkgs: dict[str, Package],
) -> None:
    log.info("Заявки и платежи...")

    # Берём первый вылет «Премиум 3 шаҳар»
    res = await db.execute(
        select(Departure)
        .where(Departure.package_id == pkgs["premium-3-shahar"].id)
        .order_by(Departure.date_out)
        .limit(1)
    )
    dep = res.scalar_one()

    booking = Booking(
        code="UM-2026-0061",
        partner_id=partners["ramaz-travel"].id,
        customer_id=customer.id,
        package_id=pkgs["premium-3-shahar"].id,
        departure_id=dep.id,
        source=BookingSource.CLICK,
        click_id="CLK-7842919",
        status=BookingStatus.NEW,
        sla_deadline_at=datetime.now(UTC) + timedelta(minutes=42),
        total_uzs=73_600_000,
        cashback_uzs=220_800,
    )
    db.add(booking)
    await db.flush()

    # Размещения: 1× DBL FM (Сардор + Мадина) + 1× SGL (Жасур)
    placement_dbl = Placement(
        booking_id=booking.id,
        room_type=RoomType.DBL_FM,
        capacity=2,
        price_per_person_uzs=23_400_000,
        total_uzs=46_800_000,
    )
    placement_sgl = Placement(
        booking_id=booking.id,
        room_type=RoomType.SGL,
        capacity=1,
        price_per_person_uzs=26_800_000,
        total_uzs=26_800_000,
    )
    db.add_all([placement_dbl, placement_sgl])
    await db.flush()

    # Привязываем паломников
    db.add_all([
        BookingPilgrim(booking_id=booking.id, pilgrim_id=pilgrims[0].id, placement_id=placement_dbl.id),
        BookingPilgrim(booking_id=booking.id, pilgrim_id=pilgrims[2].id, placement_id=placement_dbl.id),
        BookingPilgrim(booking_id=booking.id, pilgrim_id=pilgrims[1].id, placement_id=placement_sgl.id),
    ])

    # События заявки
    base_t = datetime.now(UTC) - timedelta(minutes=18)
    db.add_all([
        BookingEvent(
            booking_id=booking.id, event_type="create",
            title="Заявка создана клиентом",
            description="Сардор Раҳимов · через Click",
            actor_kind="client", actor_name="Сардор Раҳимов",
            created_at=base_t,
        ),
        BookingEvent(
            booking_id=booking.id, event_type="documents",
            title="Заполнены паспортные данные",
            description="3 загранпасорта загружены",
            actor_kind="client", actor_name="Сардор Раҳимов",
            created_at=base_t + timedelta(minutes=3),
        ),
        BookingEvent(
            booking_id=booking.id, event_type="payment",
            title="Оплачено через Click",
            description="73 600 000 сум зачислено",
            actor_kind="system",
            created_at=base_t + timedelta(minutes=6),
        ),
        BookingEvent(
            booking_id=booking.id, event_type="assigned",
            title="Поступила оператору Ramaz Travel",
            description="⏱ SLA на подтверждение 60 мин",
            actor_kind="system",
            created_at=base_t + timedelta(minutes=6, seconds=10),
        ),
    ])

    # Платёж
    payment = Payment(
        code="TR-7842919",
        booking_id=booking.id,
        customer_id=customer.id,
        partner_id=partners["ramaz-travel"].id,
        channel=PaymentChannel.CLICK,
        amount_uzs=73_600_000,
        status=PaymentStatus.SUCCESS,
        click_trans_id="CLK-7842919",
        click_phone=customer.phone,
        paid_at=base_t + timedelta(minutes=6),
    )
    db.add(payment)
    await db.flush()

    # Архивная заявка
    res2 = await db.execute(
        select(Departure)
        .where(Departure.package_id == pkgs["premium-bahor"].id)
        .order_by(Departure.date_out)
        .limit(1)
    )
    dep2 = res2.scalar_one()
    archived = Booking(
        code="UM-2025-0987",
        partner_id=partners["ramaz-travel"].id,
        customer_id=customer.id,
        package_id=pkgs["premium-bahor"].id,
        departure_id=dep2.id,
        source=BookingSource.CLICK,
        status=BookingStatus.COMPLETED,
        total_uzs=68_400_000,
        confirmed_at=datetime.now(UTC) - timedelta(days=400),
        completed_at=datetime.now(UTC) - timedelta(days=350),
    )
    db.add(archived)
    await db.flush()

    log.info("Готово: 2 demo-заявки + 1 платёж.")


# ════════════ MAIN ════════════
async def seed() -> None:
    async with AsyncSessionLocal() as db:
        await truncate_all(db)
        dirs = await seed_directories(db)
        users = await seed_umrabor_users(db)
        partners = await seed_partners(db, users["yulia.m"])
        customer, pilgrims = await seed_customer(db)
        pkgs = await seed_packages(db, partners, dirs)
        await seed_bookings(db, customer, pilgrims, partners, pkgs)
        await db.commit()

    log.info("✓ Сиды загружены. Демо-логины:")
    log.info("  super-admin UMRABOR: yulia.m / Demo-2026!")
    log.info("  партнёр (Ramaz):     ibrahim.r / Demo-2026!")
    log.info("  оператор (Ramaz):    dilfuza.t-rt / Demo-2026!")
    log.info("  клиент Mini App:     +998901234321 / OTP = 0000")


if __name__ == "__main__":
    asyncio.run(seed())
