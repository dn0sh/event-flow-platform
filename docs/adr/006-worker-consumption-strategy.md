# ADR 006: Worker Consumption Strategy

## Status

Accepted (2026-03-26)

## Context

Worker processes used `WorkerRuntime.fetch_payload()` returning `None`, so no messages were read from RabbitMQ or Kafka despite queues/topics being provisioned.

## Decision

1. **RabbitMQ (email, telegram):** After `connect()` → `channel` → `setup_topology()`, consume with `async with queue.iterator()` and `async for message`. Delegate handling to existing `RabbitMQService.process_with_retry()` for consistent ACK/NACK/DLQ behaviour.
2. **Kafka (analytics, logger):** Use `AIOKafkaConsumer` with `enable_auto_commit=False`, loop `await consumer.getmany(timeout_ms=1000, max_records=50)`, parse JSON from `msg.value`, `await handler(payload)`, then `await consumer.commit({tp: OffsetAndMetadata(msg.offset + 1, "")})` on success.
3. **Configuration:** `Settings` exposes `rabbitmq_consumer_queue`, `kafka_consumer_topic`, `kafka_consumer_group`; defaults map to `KafkaService` / `RabbitMQService` constants; Docker Compose runs one container per worker with matching command.
4. **Health:** Each worker exposes the same raw TCP HTTP health pattern on ports 8091–8094 (aligned with Compose healthchecks).

## Consequences

- **Positive:** Real end-to-end processing from brokers; observable behaviour matches architecture diagrams.
- **Negative:** `consumer_runner.py` is integration-heavy; unit coverage omits this module (see `[tool.coverage.run] omit` in `pyproject.toml`) and relies on Docker-based validation.

## Alternatives

- **Polling `fetch_payload` with REST to brokers:** rejected — not how RabbitMQ/Kafka clients are meant to be used.
- **Single worker process multiplexing all queues:** rejected — harder to scale and operate.
