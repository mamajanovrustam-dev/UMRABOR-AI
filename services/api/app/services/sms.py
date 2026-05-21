"""SMS — провайдер с моком. Боевые провайдеры (Eskiz/Playmobile) добавляются позже."""

import json
import logging
from datetime import UTC, datetime
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)


class SmsProvider:
    async def send(self, phone: str, text: str) -> bool:
        raise NotImplementedError


class MockSmsProvider(SmsProvider):
    """Логирует SMS в файл вместо реальной отправки."""

    def __init__(self, log_path: str) -> None:
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    async def send(self, phone: str, text: str) -> bool:
        entry = {
            "ts": datetime.now(UTC).isoformat(),
            "phone": phone,
            "text": text,
        }
        try:
            with self.log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError as e:
            logger.warning("Не удалось записать SMS-мок: %s", e)
        logger.info("[SMS-MOCK] %s → %s", phone, text)
        return True


def get_sms_provider() -> SmsProvider:
    if settings.SMS_PROVIDER == "mock":
        return MockSmsProvider(settings.SMS_MOCK_LOG_PATH)
    raise NotImplementedError(f"SMS-провайдер не реализован: {settings.SMS_PROVIDER}")


sms = get_sms_provider()
