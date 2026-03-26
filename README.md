# Event Flow Platform

Production-ready система обработки заказов и событий с FastAPI, Redis, RabbitMQ, Kafka, NATS, PostgreSQL, Telegram Bot и WebSocket-уведомлениями.

## Назначение проекта
- Централизованная обработка жизненного цикла заказов.
- Асинхронная публикация событий в брокеры сообщений.
- Надежная доставка уведомлений и realtime-канал для операторов.

## Быстрый старт
### Linux/macOS
```bash
cp .env.example .env
docker compose -f docker/docker-compose.yml up -d --build
python scripts/migrate.py
python scripts/seed_data.py
```

API: `http://localhost:8060/docs`  
Grafana: `http://localhost:8069`  
Prometheus: `http://localhost:8068`

## Windows (PowerShell, без make)
`make` не требуется. Для Windows используйте `scripts/task.ps1`:

```powershell
.\scripts\task.ps1 up
.\scripts\task.ps1 test
.\scripts\task.ps1 test-cov
```

Опционально можно загрузить алиасы текущей сессии:

```powershell
. .\scripts\aliases.ps1
up
test
test-cov
```

Приоритетные команды:
- Docker: `up`, `down`, `logs`
- Тесты: `test`, `test-cov`
- БД: `migrate`, `seed`
- Нагрузочные: `load-test`, `benchmark`

## Quickstart Checklist (1 day onboarding)
1. Поднять стек через Docker (`up`).
2. Применить миграции и демо-данные (`migrate`, `seed`).
3. Проверить API (`/docs`, `/health`).
4. Проверить realtime контракт (`docs/api/websocket.md`).
5. Пройти тесты и coverage gate (`test-cov`).

## Архитектура
```mermaid
flowchart TD
  API[FastAPI] --> Redis[Redis]
  API --> RabbitMQ[RabbitMQ]
  API --> Kafka[Kafka]
  API --> NATS[NATS]
  API --> Postgres[PostgreSQL]
  API --> WS[WebSocket]
  API --> TelegramBot[TelegramBot]
  RabbitMQ --> Workers[Workers]
  Kafka --> Workers
  NATS --> Workers
```

## API endpoints
- `POST /orders`
- `GET /orders`
- `GET /orders/{order_id}`
- `PATCH /orders/{order_id}/status`
- `DELETE /orders/{order_id}`
- `GET /events`
- `GET /health`
- `GET /metrics`

Примеры `curl` см. в `docs/api/openapi.md`.

## Telegram Bot команды
- `/start`
- `/orders`
- `/subscribe`
- `/status <order_id>`
- `/help`

## Безопасность
- JWT-аутентификация.
- **Production:** задайте в `.env` уникальный `JWT_SECRET` (длинная случайная строка, например `openssl rand -hex 32`). Значение по умолчанию `change-me` только для локальной разработки.
- Blacklist токенов через Redis.
- Rate limiting 100 req/min/IP.
- Секреты только через `.env`.

## Тестирование
```bash
pytest
```

Load testing:
```bash
powershell -File scripts/task.ps1 load-test
python scripts/benchmark.py
```

## Troubleshooting
- Если `load-test` падает сразу, убедитесь что API доступен на `http://localhost:8060`.
- Если `docker compose up` падает по портам, освободите диапазон `8060-8069`.
- Если Telegram Bot не стартует, проверьте `TELEGRAM_BOT_TOKEN` и `TELEGRAM_ADMIN_IDS`.
- Если CI падает на coverage, запустите `pytest --cov=src --cov-fail-under=85`.

## Дополнительная документация
- `docs/architecture.md`
- `docs/development.md`
- `docs/api/openapi.md`
- `docs/api/websocket.md`
- `docs/adr/`
