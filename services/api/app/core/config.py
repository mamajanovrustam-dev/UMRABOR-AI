from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    ENV: Literal["development", "staging", "production", "test"] = "development"
    DEBUG: bool = True
    SECRET_KEY: str = Field(min_length=32)

    ACCESS_TOKEN_TTL_MIN: int = 15
    REFRESH_TOKEN_TTL_DAYS: int = 30
    JWT_ALGORITHM: str = "HS256"

    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"

    S3_ENDPOINT: AnyHttpUrl
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET_UPLOADS: str = "umrabor-uploads"
    S3_BUCKET_VOUCHERS: str = "umrabor-vouchers"
    S3_PUBLIC_URL: AnyHttpUrl

    CLICK_MERCHANT_ID: str = "mock_merchant"
    CLICK_SERVICE_ID: str = "mock_service"
    CLICK_SECRET_KEY: str = "mock_secret"
    CLICK_MODE: Literal["mock", "sandbox", "production"] = "mock"

    SMS_PROVIDER: Literal["mock", "eskiz", "playmobile"] = "mock"
    SMS_MOCK_LOG_PATH: str = "/tmp/umrabor_sms.log"

    CORS_ORIGINS: list[str] = Field(default_factory=list)

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def split_cors(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    @property
    def is_production(self) -> bool:
        return self.ENV == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
