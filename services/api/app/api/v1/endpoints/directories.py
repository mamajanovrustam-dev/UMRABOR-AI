"""CRUD endpoints для 8 справочников. Чтение — публичное (для каталогов).
Изменение — только UMRABOR (super_admin может всё, admin тоже может править справочники)."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentUmrabor, DbSession
from app.models import (
    Airline,
    Gift,
    Hotel,
    InventoryType,
    MealType,
    PackageTypeDir,
    RejectReason,
    Service,
    TransferType,
)
from app.schemas.common import OkResponse, PageParams, Paginated
from app.schemas.directory import (
    AirlineIn,
    AirlineOut,
    GiftIn,
    GiftOut,
    HotelIn,
    HotelOut,
    InventoryTypeIn,
    InventoryTypeOut,
    ServiceIn,
    ServiceOut,
    SimpleDictIn,
    SimpleDictOut,
)

router = APIRouter()


# ════════════ Hotels ════════════
@router.get("/hotels", response_model=Paginated[HotelOut])
async def list_hotels(db: DbSession, page: int = 1, page_size: int = 50) -> Paginated[HotelOut]:
    pp = PageParams(page=page, page_size=page_size)
    total = (await db.execute(select(func.count(Hotel.id)))).scalar_one()
    res = await db.execute(
        select(Hotel).order_by(Hotel.name).offset(pp.offset).limit(pp.page_size)
    )
    return Paginated(
        items=[HotelOut.model_validate(r) for r in res.scalars().all()],
        total=total,
        page=pp.page,
        page_size=pp.page_size,
    )


@router.post("/hotels", response_model=HotelOut, status_code=status.HTTP_201_CREATED)
async def create_hotel(payload: HotelIn, db: DbSession, _: CurrentUmrabor) -> HotelOut:
    row = Hotel(**payload.model_dump())
    db.add(row)
    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Отель с таким slug уже существует") from e
    await db.refresh(row)
    return HotelOut.model_validate(row)


@router.get("/hotels/{hotel_id}", response_model=HotelOut)
async def get_hotel(hotel_id: UUID, db: DbSession) -> HotelOut:
    row = await db.get(Hotel, hotel_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Отель не найден")
    return HotelOut.model_validate(row)


@router.put("/hotels/{hotel_id}", response_model=HotelOut)
async def update_hotel(
    hotel_id: UUID, payload: HotelIn, db: DbSession, _: CurrentUmrabor
) -> HotelOut:
    row = await db.get(Hotel, hotel_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Отель не найден")
    for k, v in payload.model_dump().items():
        setattr(row, k, v)
    await db.commit()
    await db.refresh(row)
    return HotelOut.model_validate(row)


@router.delete("/hotels/{hotel_id}", response_model=OkResponse)
async def delete_hotel(hotel_id: UUID, db: DbSession, _: CurrentUmrabor) -> OkResponse:
    row = await db.get(Hotel, hotel_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Отель не найден")
    await db.delete(row)
    await db.commit()
    return OkResponse(message="Отель удалён")


# ════════════ Airlines ════════════
@router.get("/airlines", response_model=list[AirlineOut])
async def list_airlines(db: DbSession) -> list[AirlineOut]:
    res = await db.execute(select(Airline).order_by(Airline.name))
    return [AirlineOut.model_validate(r) for r in res.scalars().all()]


@router.post("/airlines", response_model=AirlineOut, status_code=status.HTTP_201_CREATED)
async def create_airline(payload: AirlineIn, db: DbSession, _: CurrentUmrabor) -> AirlineOut:
    row = Airline(**payload.model_dump())
    db.add(row)
    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "IATA-код уже занят") from e
    await db.refresh(row)
    return AirlineOut.model_validate(row)


@router.put("/airlines/{airline_id}", response_model=AirlineOut)
async def update_airline(
    airline_id: UUID, payload: AirlineIn, db: DbSession, _: CurrentUmrabor
) -> AirlineOut:
    row = await db.get(Airline, airline_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Авиакомпания не найдена")
    for k, v in payload.model_dump().items():
        setattr(row, k, v)
    await db.commit()
    await db.refresh(row)
    return AirlineOut.model_validate(row)


@router.delete("/airlines/{airline_id}", response_model=OkResponse)
async def delete_airline(airline_id: UUID, db: DbSession, _: CurrentUmrabor) -> OkResponse:
    row = await db.get(Airline, airline_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Авиакомпания не найдена")
    await db.delete(row)
    await db.commit()
    return OkResponse(message="Авиакомпания удалена")


# ════════════ Services ════════════
@router.get("/services", response_model=list[ServiceOut])
async def list_services(db: DbSession) -> list[ServiceOut]:
    res = await db.execute(select(Service).order_by(Service.name))
    return [ServiceOut.model_validate(r) for r in res.scalars().all()]


@router.post("/services", response_model=ServiceOut, status_code=status.HTTP_201_CREATED)
async def create_service(payload: ServiceIn, db: DbSession, _: CurrentUmrabor) -> ServiceOut:
    row = Service(**payload.model_dump())
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return ServiceOut.model_validate(row)


@router.put("/services/{service_id}", response_model=ServiceOut)
async def update_service(
    service_id: UUID, payload: ServiceIn, db: DbSession, _: CurrentUmrabor
) -> ServiceOut:
    row = await db.get(Service, service_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Услуга не найдена")
    for k, v in payload.model_dump().items():
        setattr(row, k, v)
    await db.commit()
    await db.refresh(row)
    return ServiceOut.model_validate(row)


@router.delete("/services/{service_id}", response_model=OkResponse)
async def delete_service(service_id: UUID, db: DbSession, _: CurrentUmrabor) -> OkResponse:
    row = await db.get(Service, service_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Услуга не найдена")
    await db.delete(row)
    await db.commit()
    return OkResponse(message="Услуга удалена")


# ════════════ Gifts ════════════
@router.get("/gifts", response_model=list[GiftOut])
async def list_gifts(db: DbSession) -> list[GiftOut]:
    res = await db.execute(select(Gift).order_by(Gift.name))
    return [GiftOut.model_validate(r) for r in res.scalars().all()]


@router.post("/gifts", response_model=GiftOut, status_code=status.HTTP_201_CREATED)
async def create_gift(payload: GiftIn, db: DbSession, _: CurrentUmrabor) -> GiftOut:
    row = Gift(**payload.model_dump())
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return GiftOut.model_validate(row)


@router.put("/gifts/{gift_id}", response_model=GiftOut)
async def update_gift(
    gift_id: UUID, payload: GiftIn, db: DbSession, _: CurrentUmrabor
) -> GiftOut:
    row = await db.get(Gift, gift_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Подарок не найден")
    for k, v in payload.model_dump().items():
        setattr(row, k, v)
    await db.commit()
    await db.refresh(row)
    return GiftOut.model_validate(row)


@router.delete("/gifts/{gift_id}", response_model=OkResponse)
async def delete_gift(gift_id: UUID, db: DbSession, _: CurrentUmrabor) -> OkResponse:
    row = await db.get(Gift, gift_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Подарок не найден")
    await db.delete(row)
    await db.commit()
    return OkResponse(message="Подарок удалён")


# ════════════ Simple dicts: meal-types, package-types, transfer-types, reject-reasons ════════════
def _simple_router(model, name_singular: str, name_plural: str) -> APIRouter:
    """Создаёт CRUD-роутер для простого справочника (name + description)."""
    sr = APIRouter()
    path = f"/{name_plural}"

    @sr.get(path, response_model=list[SimpleDictOut])
    async def _list(db: DbSession) -> list[SimpleDictOut]:
        res = await db.execute(select(model).order_by(model.name))
        return [SimpleDictOut.model_validate(r) for r in res.scalars().all()]

    @sr.post(path, response_model=SimpleDictOut, status_code=status.HTTP_201_CREATED)
    async def _create(payload: SimpleDictIn, db: DbSession, _: CurrentUmrabor) -> SimpleDictOut:
        data = payload.model_dump()
        if not hasattr(model, "icon"):
            data.pop("icon", None)
        row = model(**data)
        db.add(row)
        try:
            await db.commit()
        except IntegrityError as e:
            await db.rollback()
            raise HTTPException(
                status.HTTP_409_CONFLICT, f"{name_singular.capitalize()} уже существует"
            ) from e
        await db.refresh(row)
        return SimpleDictOut.model_validate(row)

    @sr.put(path + "/{row_id}", response_model=SimpleDictOut)
    async def _update(
        row_id: UUID, payload: SimpleDictIn, db: DbSession, _: CurrentUmrabor
    ) -> SimpleDictOut:
        row = await db.get(model, row_id)
        if row is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"{name_singular} не найден")
        data = payload.model_dump()
        if not hasattr(model, "icon"):
            data.pop("icon", None)
        for k, v in data.items():
            setattr(row, k, v)
        await db.commit()
        await db.refresh(row)
        return SimpleDictOut.model_validate(row)

    @sr.delete(path + "/{row_id}", response_model=OkResponse)
    async def _delete(row_id: UUID, db: DbSession, _: CurrentUmrabor) -> OkResponse:
        row = await db.get(model, row_id)
        if row is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"{name_singular} не найден")
        await db.delete(row)
        await db.commit()
        return OkResponse(message=f"{name_singular.capitalize()} удалён")

    return sr


router.include_router(_simple_router(MealType, "тип питания", "meal-types"))
router.include_router(_simple_router(PackageTypeDir, "тип пакета", "package-types"))
router.include_router(_simple_router(TransferType, "тип трансфера", "transfer-types"))
router.include_router(_simple_router(RejectReason, "причина отказа", "reject-reasons"))


# ════════════ Inventory Types ════════════
@router.get("/inventory-types", response_model=list[InventoryTypeOut])
async def list_inventory_types(db: DbSession) -> list[InventoryTypeOut]:
    res = await db.execute(select(InventoryType).order_by(InventoryType.sort_order))
    return [InventoryTypeOut.model_validate(r) for r in res.scalars().all()]


@router.post(
    "/inventory-types", response_model=InventoryTypeOut, status_code=status.HTTP_201_CREATED
)
async def create_inventory_type(
    payload: InventoryTypeIn, db: DbSession, _: CurrentUmrabor
) -> InventoryTypeOut:
    row = InventoryType(**payload.model_dump())
    db.add(row)
    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Тип с таким кодом уже существует") from e
    await db.refresh(row)
    return InventoryTypeOut.model_validate(row)


@router.put("/inventory-types/{row_id}", response_model=InventoryTypeOut)
async def update_inventory_type(
    row_id: UUID, payload: InventoryTypeIn, db: DbSession, _: CurrentUmrabor
) -> InventoryTypeOut:
    row = await db.get(InventoryType, row_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Тип не найден")
    for k, v in payload.model_dump().items():
        setattr(row, k, v)
    await db.commit()
    await db.refresh(row)
    return InventoryTypeOut.model_validate(row)
