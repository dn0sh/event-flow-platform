import asyncio

import pytest

from src.api.websocket import notifications as ws_module


@pytest.mark.asyncio
async def test_stop_nats_bridge_noop_when_none() -> None:
    await ws_module.stop_nats_bridge(None)


@pytest.mark.asyncio
async def test_stop_nats_bridge_drains_subscription_and_client() -> None:
    class FakeSub:
        def __init__(self) -> None:
            self.drained = False

        async def drain(self) -> None:
            self.drained = True

    class FakeClient:
        def __init__(self) -> None:
            self.drained = False
            self.closed = False

        async def drain(self) -> None:
            self.drained = True

        async def close(self) -> None:
            self.closed = True

    async def short_keepalive() -> None:
        await asyncio.sleep(0.01)

    task = asyncio.create_task(short_keepalive())
    res = ws_module.NatsBridgeResources(
        client=FakeClient(), subscription=FakeSub(), keepalive_task=task
    )
    await ws_module.stop_nats_bridge(res)
    assert res.subscription.drained
    assert res.client.drained
    assert res.client.closed


@pytest.mark.asyncio
async def test_start_nats_bridge_success(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeSub:
        async def drain(self) -> None:
            pass

    class FakeClient:
        async def subscribe(self, subject: str, cb: object) -> FakeSub:
            return FakeSub()

    async def fake_connect() -> FakeClient:
        return FakeClient()

    monkeypatch.setattr(ws_module.nats_service, "connect", fake_connect)
    bridge = await ws_module.start_nats_realtime_bridge()
    assert bridge is not None
    await ws_module.stop_nats_bridge(bridge)
