import asyncio

import pytest

from src.workers.runtime import WorkerRuntime


@pytest.mark.asyncio
async def test_worker_runtime_idempotency():
    calls = []

    async def handler(payload):
        calls.append(payload["id"])

    runtime = WorkerRuntime(name="test-worker", process_handler=handler, poll_interval_seconds=0.01)
    payload = {"id": "m-1"}
    await runtime.process_with_retry(payload)
    await runtime.process_with_retry(payload)
    assert calls == ["m-1"]


@pytest.mark.asyncio
async def test_worker_runtime_retry_success_after_failure():
    state = {"count": 0}

    async def handler(_payload):
        state["count"] += 1
        if state["count"] < 2:
            raise RuntimeError("temporary error")

    runtime = WorkerRuntime(name="test-worker", process_handler=handler, poll_interval_seconds=0.01)
    await runtime.process_with_retry({"id": "m-2"})
    assert state["count"] == 2


@pytest.mark.asyncio
async def test_worker_runtime_run_stops(monkeypatch):
    async def handler(_payload):
        return None

    runtime = WorkerRuntime(name="test-worker", process_handler=handler, poll_interval_seconds=0.01)

    async def fake_fetch():
        runtime.stop_event.set()
        return None

    monkeypatch.setattr(runtime, "fetch_payload", fake_fetch)
    await runtime.run()
    assert runtime.stop_event.is_set()


@pytest.mark.asyncio
async def test_worker_health_handler_response():
    async def handler(_payload):
        return None

    runtime = WorkerRuntime(name="test-worker", process_handler=handler, poll_interval_seconds=0.01)
    reader = asyncio.StreamReader()

    class Writer:
        def __init__(self):
            self.data = b""
            self.closed = False

        def write(self, data):
            self.data += data

        async def drain(self):
            return None

        def close(self):
            self.closed = True

        async def wait_closed(self):
            return None

    writer = Writer()
    await runtime._health_handler(reader, writer)
    assert b"200 OK" in writer.data
