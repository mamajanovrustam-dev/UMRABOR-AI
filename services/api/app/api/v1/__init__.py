"""API v1 router aggregation."""

from fastapi import APIRouter

api_router = APIRouter()

# Роутеры подключаются в Sprint 1 (auth, partners, packages, bookings, ...)
# Пример:
# from app.api.v1.endpoints import auth, partners
# api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
# api_router.include_router(partners.router, prefix="/partners", tags=["partners"])
