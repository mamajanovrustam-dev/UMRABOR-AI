"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, directories

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(directories.router, prefix="/directories", tags=["directories"])
