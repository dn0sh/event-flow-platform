# ADR 004: NATS Pub/Sub

## Статус
accepted

## Контекст
Realtime-уведомления (WebSocket push), presence и сервисные health-события требуют низкой задержки и легковесного pub/sub.

## Решение
NATS subjects:
- `notifications.realtime`;
- `presence.online`;
- `system.health`;
- JetStream опционально по флагу `NATS_USE_JETSTREAM`.

## Последствия
- Низкая latency для fan-out событий.
- Дополнительный компонент в инфраструктуре.

## Альтернативы
- Redis pub/sub (менее устойчиво при сложном routing).
- Kafka-only push (избыточная стоимость для ultra-low latency realtime).
