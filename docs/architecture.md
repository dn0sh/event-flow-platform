# Architecture

## System context

```mermaid
flowchart TD
  ClientApps[ClientApps] --> ApiLayer[FastAPI_API]
  Operators[Operators] --> TelegramBot[TelegramBot]
  ApiLayer --> PostgreSQL[PostgreSQL]
  ApiLayer --> Redis[Redis]
  ApiLayer --> RabbitMQ[RabbitMQ]
  ApiLayer --> Kafka[Kafka]
  ApiLayer --> NATS[NATS]
  ApiLayer --> WebSocketGateway[WebSocketGateway]
  RabbitMQ --> WorkerPool[Workers]
  Kafka --> WorkerPool
  NATS --> WorkerPool
  ApiLayer --> Prometheus[Prometheus]
  Prometheus --> Grafana[Grafana]
```

## Event flow

```mermaid
flowchart LR
  CreateOrder[POST_/orders] --> PersistOrder[Persist_in_PostgreSQL]
  PersistOrder --> KafkaOrderEvents[Kafka_order.events]
  PersistOrder --> RabbitPending[Rabbit_orders.pending]
  PersistOrder --> NatsRealtime[NATS_notifications.realtime]
  KafkaOrderEvents --> AnalyticsConsumer[analytics-consumer]
  KafkaOrderEvents --> LoggerConsumer[logger-consumer]
  RabbitPending --> EmailWorker[EmailWorker]
  RabbitPending --> TelegramWorker[TelegramWorker]
  NatsRealtime --> WsPush[WebSocket_room_push]
```

## Observability
- Prometheus собирает метрики API и инфраструктуры.
- Grafana импортирует dashboards автоматически из `docker/grafana/dashboards`.
- Обязательные панели: API latency, queue depth, error rate.
- Datasource в provisioning задаётся с `uid: prometheus`, чтобы JSON-дашборды ссылались на один и тот же источник.

## Lessons learned (1.1.0)
- Жизненный цикл FastAPI лучше выражать через `lifespan`, а NATS-клиент закрывать через `drain`/`close`, а не только отменой задачи.
- Потребление из брокеров вынесено в отдельный слой (`consumer_runner`); покрытие этого модуля в unit-тестах заменено проверкой в Docker.
