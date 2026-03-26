from __future__ import annotations

import json
from datetime import timedelta
from typing import Any

import aio_pika
from aio_pika.abc import AbstractChannel, AbstractIncomingMessage, AbstractRobustConnection
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config.settings import get_settings

settings = get_settings()


class RabbitMQService:
    ORDERS_PENDING = "orders.pending"
    NOTIFICATIONS_EMAIL = "notifications.email"
    NOTIFICATIONS_TELEGRAM = "notifications.telegram"

    @retry(
        stop=stop_after_attempt(20),
        wait=wait_exponential(multiplier=1.5, min=2, max=30),
    )
    async def connect(self) -> AbstractRobustConnection:
        return await aio_pika.connect_robust(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
            login=settings.rabbitmq_user,
            password=settings.rabbitmq_password,
        )

    async def setup_topology(self, channel: AbstractChannel) -> None:
        orders_dlx = await channel.declare_exchange(
            "orders.dlx", aio_pika.ExchangeType.DIRECT, durable=True
        )
        notifications_dlx = await channel.declare_exchange(
            "notifications.dlx", aio_pika.ExchangeType.DIRECT, durable=True
        )

        await channel.declare_queue(
            self.ORDERS_PENDING,
            durable=True,
            arguments={
                "x-max-priority": 10,
                "x-dead-letter-exchange": orders_dlx.name,
                "x-dead-letter-routing-key": "orders.failed",
            },
        )
        await channel.declare_queue(
            self.NOTIFICATIONS_EMAIL,
            durable=True,
            arguments={
                "x-dead-letter-exchange": notifications_dlx.name,
                "x-dead-letter-routing-key": "notifications.email.failed",
            },
        )
        await channel.declare_queue(
            self.NOTIFICATIONS_TELEGRAM,
            durable=True,
            arguments={
                "x-dead-letter-exchange": notifications_dlx.name,
                "x-dead-letter-routing-key": "notifications.telegram.failed",
            },
        )
        await channel.declare_queue("orders.failed", durable=True)
        await channel.declare_queue("notifications.email.failed", durable=True)
        await channel.declare_queue("notifications.telegram.failed", durable=True)

    async def publish_json(
        self,
        channel: AbstractChannel,
        queue_name: str,
        payload: dict[str, Any],
        priority: int = 0,
    ) -> None:
        body = json.dumps(payload).encode("utf-8")
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=body,
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                priority=priority,
            ),
            routing_key=queue_name,
        )

    async def process_with_retry(
        self,
        message: AbstractIncomingMessage,
        handler: Any,
        max_retries: int = 3,
    ) -> None:
        headers = message.headers or {}
        retry_raw = headers.get("x-retry-count", 0)
        retry_count = int(retry_raw) if isinstance(retry_raw, (int, str)) else 0

        try:
            payload = json.loads(message.body.decode("utf-8"))
            await handler(payload)
            await message.ack()
        except Exception:
            if retry_count < max_retries:
                next_headers = dict(headers)
                next_headers["x-retry-count"] = retry_count + 1
                delay_ms = int(timedelta(seconds=2**retry_count).total_seconds() * 1000)
                next_headers["x-delay"] = delay_ms
                await message.nack(requeue=True)
            else:
                await message.reject(requeue=False)
