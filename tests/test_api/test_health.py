import pytest
from fastapi.responses import StreamingResponse
from jose import jwt
from starlette.websockets import WebSocketDisconnect

from src.api.routes.events import _stream_events, stream_events
from src.api.websocket import notifications as ws_module
from src.api.websocket.notifications import ConnectionManager, _verify_jwt, websocket_notifications
from src.config.settings import get_settings


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()


@pytest.mark.asyncio
async def test_events_endpoint_returns_stream():
    response = await stream_events()
    assert isinstance(response, StreamingResponse)


@pytest.mark.asyncio
async def test_ws_connection_manager_publish():
    manager = ConnectionManager()

    class DummyWs:
        def __init__(self):
            self.messages = []

        async def accept(self):
            return None

        async def send_text(self, message: str):
            self.messages.append(message)

    ws = DummyWs()
    await manager.connect(ws)
    manager.subscribe(ws, "o-1")
    await manager.publish("o-1", "hello")
    manager.unsubscribe(ws, "o-1")
    manager.disconnect(ws)
    assert ws.messages == ["hello"]


@pytest.mark.asyncio
async def test_stream_generator_single_item():
    generator = _stream_events()
    first = await generator.__anext__()
    assert "heartbeat" in first


@pytest.mark.asyncio
async def test_ws_endpoint_disconnect_path():
    settings = get_settings()
    token = jwt.encode({"sub": "tester"}, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    class DummyWs:
        def __init__(self):
            self.query_params = {"token": token}
            self.closed = False

        async def accept(self):
            return None

        async def receive_text(self):
            raise WebSocketDisconnect()

        async def close(self, code: int):
            self.closed = True

    ws = DummyWs()
    await websocket_notifications(ws)


def test_verify_jwt():
    settings = get_settings()
    token = jwt.encode({"sub": "tester"}, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    payload = _verify_jwt(token)
    assert payload["sub"] == "tester"


@pytest.mark.asyncio
async def test_start_nats_bridge_failure(monkeypatch):
    async def _fail_connect():
        raise RuntimeError("nats down")

    monkeypatch.setattr(ws_module.nats_service, "connect", _fail_connect)
    task = await ws_module.start_nats_realtime_bridge()
    assert task is None
