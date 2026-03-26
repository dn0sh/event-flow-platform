from __future__ import annotations

import json
from typing import Any, cast

import httpx
from aiormq.exceptions import AMQPError
from structlog import get_logger

from src.config.settings import get_settings
from src.services.rabbitmq_service import RabbitMQService

logger = get_logger(__name__)
settings = get_settings()


def _log_api_http_warning(response: httpx.Response) -> None:
    if response.is_success:
        return
    logger.warning(
        "api_http_error",
        method=response.request.method,
        url=str(response.request.url),
        status_code=response.status_code,
        body=response.text[:2000],
    )


class BotApiClient:
    def __init__(self, base_url: str | None = None) -> None:
        self._base_url = base_url or settings.api_base_url

    async def list_orders(self, limit: int = 5) -> list[dict[str, Any]] | None:
        """None — API недоступен (сеть, таймаут, 5xx и т.д.)."""
        try:
            async with httpx.AsyncClient(base_url=self._base_url, timeout=10) as client:
                response = await client.get("/orders", params={"limit": limit, "offset": 0})
                if response.is_error:
                    _log_api_http_warning(response)
                    return None
                payload = response.json()
                return cast(list[dict[str, Any]], payload.get("items", []))
        except httpx.RequestError as exc:
            logger.warning("api_unreachable", error=str(exc), base_url=self._base_url)
            return None
        except json.JSONDecodeError as exc:
            logger.warning("api_bad_json", error=str(exc))
            return None

    async def get_order_status(self, order_id: str) -> str | None:
        """None — сеть/сервер; иначе статус или «не найден» при HTTP 404."""
        try:
            async with httpx.AsyncClient(base_url=self._base_url, timeout=10) as client:
                response = await client.get(f"/orders/{order_id}")
                if response.status_code == 404:
                    return "не найден"
                if response.is_error:
                    _log_api_http_warning(response)
                    return None
                payload = response.json()
                return str(payload.get("status", "unknown"))
        except httpx.RequestError as exc:
            logger.warning("api_unreachable", error=str(exc), base_url=self._base_url)
            return None
        except json.JSONDecodeError as exc:
            logger.warning("api_bad_json", error=str(exc))
            return None


class BotNotificationPublisher:
    def __init__(self) -> None:
        self._rabbit = RabbitMQService()

    async def publish_telegram_notification(self, payload: dict[str, Any]) -> bool:
        """False — не удалось достучаться до RabbitMQ (сеть/брокер)."""
        try:
            connection = await self._rabbit.connect()
            channel = await connection.channel()
            await self._rabbit.setup_topology(channel)
            await self._rabbit.publish_json(channel, self._rabbit.NOTIFICATIONS_TELEGRAM, payload)
            await connection.close()
            logger.info("telegram_notification_enqueued", queue=self._rabbit.NOTIFICATIONS_TELEGRAM)
            return True
        except AMQPError as exc:
            logger.warning("rabbitmq_unreachable", error=str(exc))
            return False
        except OSError as exc:
            logger.warning("rabbitmq_unreachable", error=str(exc))
            return False
