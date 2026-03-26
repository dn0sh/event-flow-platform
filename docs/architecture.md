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
