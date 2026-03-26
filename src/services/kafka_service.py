import json
from typing import Any, cast

import httpx
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer  # type: ignore[import-untyped]
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config.settings import get_settings

settings = get_settings()


class KafkaService:
    ORDER_EVENTS_TOPIC = "order.events"
    AUDIT_LOG_TOPIC = "audit.log"
    ANALYTICS_GROUP = "analytics-consumer"
    LOGGER_GROUP = "logger-consumer"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    async def build_producer(self) -> AIOKafkaProducer:
        producer = AIOKafkaProducer(bootstrap_servers=settings.kafka_bootstrap_servers)
        await producer.start()
        return producer

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    async def build_consumer(self, topic: str, group_id: str) -> AIOKafkaConsumer:
        consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id=group_id,
            enable_auto_commit=False,
            auto_offset_reset="earliest",
        )
        await consumer.start()
        return consumer

    async def publish_event(
        self, producer: AIOKafkaProducer, topic: str, payload: dict[str, Any]
    ) -> None:
        await producer.send_and_wait(topic, json.dumps(payload).encode("utf-8"))

    async def publish_order_event(
        self, producer: AIOKafkaProducer, payload: dict[str, Any]
    ) -> None:
        await self.publish_event(producer, self.ORDER_EVENTS_TOPIC, payload)

    async def publish_audit_log(
        self, producer: AIOKafkaProducer, payload: dict[str, Any]
    ) -> None:
        await self.publish_event(producer, self.AUDIT_LOG_TOPIC, payload)

    async def register_schema(self, subject: str, schema: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{settings.schema_registry_url}/subjects/{subject}/versions",
                json={"schema": json.dumps(schema)},
            )
            response.raise_for_status()
            return cast(dict[str, Any], response.json())
