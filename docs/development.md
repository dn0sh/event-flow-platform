# Development Guide

## Requirements
- Python 3.11+
- Docker Desktop (Linux containers)
- Git, PowerShell 7+ (Windows) или bash (Linux/macOS)

## Bootstrap in 15 minutes
1. Скопировать окружение: `cp .env.example .env` (или `copy .env.example .env` в Windows CMD).
2. Поднять стек:
   - Linux/macOS: `make up`
   - Windows PowerShell: `.\scripts\task.ps1 up`
3. Применить миграции:
   - Linux/macOS: `make migrate`
   - Windows: `.\scripts\task.ps1 migrate`
4. Заполнить демо-данные:
   - Linux/macOS: `make seed`
   - Windows: `.\scripts\task.ps1 seed`
5. Проверить: `http://localhost:8060/health`, `http://localhost:8060/docs`.

## Local development loop
- API hot-reload: `bash scripts/dev.sh`
- Tests: `pytest -q`
- Coverage: `pytest --cov=src --cov-fail-under=85`
- Lint + typecheck: `black --check . && isort --check-only . && flake8 src tests && mypy src`

## Troubleshooting
- **Port already used:** убедитесь, что `8060-8069` свободны.
- **Redis/RabbitMQ/Kafka not reachable:** проверьте `docker compose ps` и healthchecks.
- **Telegram bot not responding:** проверьте `TELEGRAM_BOT_TOKEN` и логи `bot` сервиса.
- **Coverage gate failed:** добавьте unit tests в `tests/test_api`, `tests/test_services`, `tests/test_bot`.
