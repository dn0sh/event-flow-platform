# ADR 003: Kafka Events

## Статус
accepted

## Контекст
Необходимы event streaming, replay и аудит (комплаенс) с ретеншеном 30 дней.

## Решение
Kafka для event stream:
- topics: `order.events`, `audit.log`;
- consumer groups: `analytics-consumer`, `logger-consumer`;
- retention policy: 30 days;
- schema versioning через Schema Registry.

## Последствия
- Высокая пропускная способность и replay capability.
- Более высокий операционный порог (Kafka + Schema Registry).

## Альтернативы
- RabbitMQ streams.
- PostgreSQL outbox-only (ограниченный replay и analytics scale).
