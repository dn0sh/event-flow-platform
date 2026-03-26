from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from src.api.middleware.rate_limiter import RateLimitMiddleware
from src.api.routes.events import router as events_router
from src.api.routes.health import router as health_router
from src.api.routes.orders import router as orders_router
from src.api.websocket.notifications import router as websocket_router
from src.api.websocket.notifications import (
    start_nats_realtime_bridge,
    stop_nats_bridge,
)
from src.config.logging import configure_logging
from src.config.settings import get_settings

settings = get_settings()
configure_logging(settings.log_level)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    bridge = await start_nats_realtime_bridge()
    yield
    await stop_nats_bridge(bridge)


app = FastAPI(title="Event Flow Platform", version="1.1.0", lifespan=lifespan)
app.add_middleware(RateLimitMiddleware)

app.include_router(orders_router)
app.include_router(events_router)
app.include_router(health_router)
app.include_router(websocket_router)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.get("/")
async def root() -> dict[str, str]:
    return {"service": "event-flow-platform", "status": "ok"}
