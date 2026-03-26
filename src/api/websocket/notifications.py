import asyncio
import json
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, cast

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt  # type: ignore[import-untyped]
from structlog import get_logger

from src.config.settings import get_settings
from src.services.nats_service import NatsService

router = APIRouter()
settings = get_settings()
logger = get_logger(__name__)
nats_service = NatsService()


class ConnectionManager:
    def __init__(self) -> None:
        self.rooms: dict[str, set[WebSocket]] = defaultdict(set)
        self.socket_rooms: dict[WebSocket, set[str]] = defaultdict(set)

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()

    def subscribe(self, websocket: WebSocket, order_id: str) -> None:
        self.rooms[order_id].add(websocket)
        self.socket_rooms[websocket].add(order_id)

    def disconnect(self, websocket: WebSocket) -> None:
        for order_id in list(self.socket_rooms.get(websocket, set())):
            self.rooms[order_id].discard(websocket)
            if not self.rooms[order_id]:
                self.rooms.pop(order_id, None)
        self.socket_rooms.pop(websocket, None)

    def unsubscribe(self, websocket: WebSocket, order_id: str) -> None:
        self.rooms[order_id].discard(websocket)
        if not self.rooms[order_id]:
            self.rooms.pop(order_id, None)
        self.socket_rooms[websocket].discard(order_id)
        if not self.socket_rooms[websocket]:
            self.socket_rooms.pop(websocket, None)

    async def publish(self, order_id: str, message: str) -> None:
        for ws in list(self.rooms.get(order_id, set())):
            await ws.send_text(message)


manager = ConnectionManager()


def _verify_jwt(token: str) -> dict[str, Any]:
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    return cast(dict[str, Any], payload)


@router.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket) -> None:
    token = websocket.query_params.get("token", "")
    if not token:
        await websocket.close(code=1008)
        return
    try:
        _verify_jwt(token)
    except JWTError:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
                continue

            payload = json.loads(data)
            action = payload.get("action")
            order_id = str(payload.get("order_id", "")).strip()
            if action == "subscribe" and order_id:
                manager.subscribe(websocket, order_id)
                await websocket.send_text(json.dumps({"type": "subscribed", "order_id": order_id}))
            elif action == "unsubscribe" and order_id:
                manager.unsubscribe(websocket, order_id)
                await websocket.send_text(
                    json.dumps({"type": "unsubscribed", "order_id": order_id})
                )
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@dataclass
class NatsBridgeResources:
    client: Any
    subscription: Any
    keepalive_task: asyncio.Task[Any]


async def start_nats_realtime_bridge() -> NatsBridgeResources | None:
    try:
        client = await nats_service.connect()

        async def _handler(msg: Any) -> None:
            payload = json.loads(msg.data.decode("utf-8"))
            order_id = str(payload.get("order_id", ""))
            if order_id:
                await manager.publish(order_id, msg.data.decode("utf-8"))

        subscription = await client.subscribe(nats_service.REALTIME_SUBJECT, cb=_handler)

        async def _keep_alive() -> None:
            while True:
                await asyncio.sleep(3600)

        keepalive_task = asyncio.create_task(_keep_alive())
        return NatsBridgeResources(
            client=client, subscription=subscription, keepalive_task=keepalive_task
        )
    except Exception:
        logger.exception("nats_bridge_start_failed")
        return None


async def stop_nats_bridge(resources: NatsBridgeResources | None) -> None:
    if resources is None:
        return
    resources.keepalive_task.cancel()
    try:
        await resources.keepalive_task
    except asyncio.CancelledError:
        pass
    try:
        if resources.subscription is not None:
            await resources.subscription.drain()
    except Exception:
        logger.exception("nats_subscription_drain_failed")
    try:
        if resources.client is not None:
            await resources.client.drain()
            await resources.client.close()
    except Exception:
        logger.exception("nats_client_close_failed")
