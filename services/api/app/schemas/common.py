"""Общие Pydantic-схемы."""

from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TimestampedSchema(BaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime


class Paginated(BaseSchema, Generic[T]):
    items: list[T]
    total: int
    page: int = 1
    page_size: int = 20


class PageParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class OkResponse(BaseModel):
    ok: bool = True
    message: str | None = None
