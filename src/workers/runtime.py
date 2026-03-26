from __future__ import annotations

import asyncio
import json
import signal
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

import pybreaker
from structlog import get_logger
from tenacity import retry, stop_after_attempt, wait_exponential

logger = get_logger(__name__)


@dataclass
class WorkerRuntime:
    name: str
    process_handler: Callable[[dict[str, Any]], Awaitable[None]]
    health_port: int = 8090
    poll_interval_seconds: float = 1.0
    stop_event: asyncio.Event = field(default_factory=asyncio.Event)
    processed_message_ids: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        self.breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30)
        self._health_server: asyncio.base_events.Server | None = None

    async def _health_handler(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        _ = reader
        payload = json.dumps({"worker": self.name, "status": "ok"}).encode("utf-8")
        writer.write(
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: application/json\r\n"
            + f"Content-Length: {len(payload)}\r\n\r\n".encode("utf-8")
            + payload
        )
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def start_healthcheck_server(self) -> None:
        self._health_server = await asyncio.start_server(
            self._health_handler, host="0.0.0.0", port=self.health_port
        )
        logger.info("worker_health_started", worker=self.name, port=self.health_port)

    async def stop_healthcheck_server(self) -> None:
        if self._health_server is not None:
            self._health_server.close()
            await self._health_server.wait_closed()
            self._health_server = None

    def register_signal_handlers(self) -> None:
        loop = asyncio.get_running_loop()

        def _stop() -> None:
            logger.info("worker_stop_signal_received", worker=self.name)
            self.stop_event.set()

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, _stop)
            except NotImplementedError:
                pass

    async def fetch_payload(self) -> dict[str, Any] | None:
        return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    async def process_with_retry(self, payload: dict[str, Any]) -> None:
        message_id = str(payload.get("id", ""))
        if message_id and message_id in self.processed_message_ids:
            logger.info("worker_message_skipped_duplicate", worker=self.name, message_id=message_id)
            return

        self.breaker.call(lambda: True)
        await self.process_handler(payload)
        if message_id:
            self.processed_message_ids.add(message_id)
        logger.info("worker_message_processed", worker=self.name, message_id=message_id)

    async def run(self) -> None:
        await self.start_healthcheck_server()
        self.register_signal_handlers()
        logger.info("worker_started", worker=self.name)
        try:
            while not self.stop_event.is_set():
                payload = await self.fetch_payload()
                if payload is not None:
                    try:
                        await self.process_with_retry(payload)
                    except Exception:
                        logger.exception("worker_payload_processing_failed", worker=self.name)
                await asyncio.sleep(self.poll_interval_seconds)
        finally:
            await self.stop_healthcheck_server()
            logger.info("worker_stopped", worker=self.name)
