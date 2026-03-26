# ADR 002: RabbitMQ Queues

## Статус
accepted

## Контекст
Асинхронные задачи (email/telegram notifications) требуют надежной доставки и контроль ошибок с повторной обработкой.

## Решение
RabbitMQ как task broker:
- очереди `orders.pending`, `notifications.email`, `notifications.telegram`;
- ACK/NACK;
- retry до 3 попыток с exponential backoff;
- DLQ для poison messages;
- priority queue для VIP-заказов.

## Последствия
- Надежная обработка фоновых задач.
- Более сложная эксплуатация: topology, dead letters, monitoring queue depth.

## Альтернативы
- Kafka-only queueing (хуже для классической task semantics).
- Celery default setup (меньше контроля на уровне topology).
