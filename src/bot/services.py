from __future__ import annotations

from typing import Any, cast

import httpx
from structlog import get_logger

from src.config.settings import get_settings
from src.services.rabbitmq_service import RabbitMQService

logger = get_logger(__name__)
settings = get_settings()


class BotApiClient:
    def __init__(self, base_url: str | None = None) -> None:
        self._base_url = base_url or settings.api_base_url

    async def list_orders(self, limit: int = 5) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(base_url=self._base_url, timeout=10) as client:
            response = await client.get("/orders", params={"limit": limit, "offset": 0})
            response.raise_for_status()
            payload = response.json()
            return cast(list[dict[str, Any]], payload.get("items", []))

    async def get_order_status(self, order_id: str) -> str:
        async with httpx.AsyncClient(base_url=self._base_url, timeout=10) as client:
            response = await client.get(f"/orders/{order_id}")
            response.raise_for_status()
            payload = response.json()
            return str(payload.get("status", "unknown"))


class BotNotificationPublisher:
    def __init__(self) -> None:
        self._rabbit = RabbitMQService()

    async def publish_telegram_notification(self, payload: dict[str, Any]) -> None:
        connection = await self._rabbit.connect()
        channel = await connection.channel()
        await self._rabbit.setup_topology(channel)
        await self._rabbit.publish_json(channel, self._rabbit.NOTIFICATIONS_TELEGRAM, payload)
        await connection.close()
        logger.info("telegram_notification_enqueued", queue=self._rabbit.NOTIFICATIONS_TELEGRAM)
