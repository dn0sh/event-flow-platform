# ADR 005: FastAPI Lifespan Pattern

## Status

Accepted (2026-03-26)

## Context

Startup and shutdown logic lived in deprecated `@app.on_event("startup")` / `"shutdown"`. FastAPI recommends `lifespan` context managers for predictable resource acquisition and teardown order.

The NATS realtime bridge used a global `asyncio.Task` cancelled on shutdown without draining the NATS client or subscription, risking stuck connections.

## Decision

1. Replace `on_event` with a single `@asynccontextmanager` `lifespan` passed to `FastAPI(lifespan=...)`.
2. On startup, call `start_nats_realtime_bridge()` and keep returned `NatsBridgeResources` (client, subscription, keepalive task).
3. On shutdown, call `stop_nats_bridge(resources)`: cancel keepalive task, `await subscription.drain()`, then `await client.drain()` and `await client.close()`.

## Consequences

- **Positive:** Aligns with Starlette/FastAPI guidance; no deprecation warnings for lifecycle hooks; ordered cleanup of NATS.
- **Negative:** Slightly more code in `notifications.py`; tests must mock bridge resources for full shutdown paths.

## Alternatives

- **Keep `on_event`:** rejected — deprecated API surface.
- **Only cancel task, no NATS drain:** rejected — leaves sockets half-open under load.
