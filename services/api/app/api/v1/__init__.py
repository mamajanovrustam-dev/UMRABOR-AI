"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    audit,
    auth,
    bookings,
    dashboard,
    directories,
    packages,
    partners,
    payments,
    pilgrims,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(partners.router, prefix="/partners", tags=["partners"])
api_router.include_router(packages.router, prefix="/packages", tags=["packages"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(pilgrims.router, prefix="/pilgrims", tags=["pilgrims"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(directories.router, prefix="/directories", tags=["directories"])
