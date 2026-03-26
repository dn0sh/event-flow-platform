"""RabbitMQ and Kafka consumer loops with health HTTP and graceful shutdown."""

from __future__ import annotations

import asyncio
import json
import signal
from collections.abc import Awaitable, Callable
from typing import Any

from aiokafka import AIOKafkaConsumer  # type: ignore[import-untyped]
from aiokafka.errors import KafkaError  # type: ignore[import-untyped]
from aiokafka.structs import OffsetAndMetadata  # type: ignore[import-untyped]
from structlog import get_logger

from src.config.settings import get_settings
from src.services.rabbitmq_service import RabbitMQService

logger = get_logger(__name__)


async def _health_handler(
    worker_name: str, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
) -> None:
    _ = reader
    payload = json.dumps({"worker": worker_name, "status": "ok"}).encode("utf-8")
    writer.write(
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: application/json\r\n"
        + f"Content-Length: {len(payload)}\r\n\r\n".encode("utf-8")
        + payload
    )
    await writer.drain()
    writer.close()
    await writer.wait_closed()


def _install_signal_handlers(stop_event: asyncio.Event) -> None:
    loop = asyncio.get_running_loop()

    def _handler() -> None:
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _handler)
        except NotImplementedError:
            pass


async def run_rabbitmq_consumer(
    queue_name: str,
    handler: Callable[[dict[str, Any]], Awaitable[None]],
    *,
    health_port: int,
    worker_name: str,
) -> None:
    stop_event = asyncio.Event()
    _install_signal_handlers(stop_event)

    async def _health(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        await _health_handler(worker_name, reader, writer)

    health_server = await asyncio.start_server(_health, host="0.0.0.0", port=health_port)
    logger.info("worker_health_started", worker=worker_name, port=health_port)

    svc = RabbitMQService()
    connection = await svc.connect()
    channel = await connection.channel()
    await svc.setup_topology(channel)
    try:
        queue = await channel.declare_queue(queue_name, passive=True)
    except Exception:
        queue = await channel.declare_queue(queue_name, durable=True)

    try:
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                if stop_event.is_set():
                    break
                await svc.process_with_retry(message, handler)
    finally:
        health_server.close()
        await health_server.wait_closed()
        await channel.close()
        await connection.close()
        logger.info("worker_stopped", worker=worker_name)


async def run_kafka_consumer(
    topic: str,
    group_id: str,
    handler: Callable[[dict[str, Any]], Awaitable[None]],
    *,
    health_port: int,
    worker_name: str,
) -> None:
    settings = get_settings()
    stop_event = asyncio.Event()
    _install_signal_handlers(stop_event)

    async def _health(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        await _health_handler(worker_name, reader, writer)

    health_server = await asyncio.start_server(_health, host="0.0.0.0", port=health_port)
    logger.info("worker_health_started", worker=worker_name, port=health_port)

    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=group_id,
        enable_auto_commit=False,
        auto_offset_reset="earliest",
        value_deserializer=lambda v: v,
    )
    await consumer.start()
    try:
        while not stop_event.is_set():
            try:
                records = await consumer.getmany(timeout_ms=1000, max_records=50)
            except KafkaError as exc:
                logger.warning("kafka_getmany", error=str(exc))
                await asyncio.sleep(0.5)
                continue
            if not records:
                continue
            for tp, messages in records.items():
                for msg in messages:
                    if stop_event.is_set():
                        break
                    try:
                        raw = msg.value
                        if isinstance(raw, bytes):
                            payload = json.loads(raw.decode())
                        else:
                            payload = json.loads(str(raw))
                    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                        logger.warning("kafka_bad_payload", error=str(exc))
                        try:
                            await consumer.commit({tp: OffsetAndMetadata(msg.offset + 1, "")})
                        except KafkaError as cexc:
                            logger.warning("kafka_commit_failed", error=str(cexc))
                        continue
                    try:
                        await handler(payload)
                    except Exception:
                        logger.exception("kafka_handler_failed")
                        continue
                    try:
                        await consumer.commit({tp: OffsetAndMetadata(msg.offset + 1, "")})
                    except KafkaError as cexc:
                        logger.warning("kafka_commit_failed", error=str(cexc))
    finally:
        health_server.close()
        await health_server.wait_closed()
        await consumer.stop()
        logger.info("worker_stopped", worker=worker_name)
