# Contributing

## Локальный запуск
1. `cp .env.example .env`
2. `docker compose -f docker/docker-compose.yml up -d --build`

## Стандарты
- Python 3.11+
- Type hints обязательно
- `mypy --strict`
- Форматирование: `black`, `isort`
- Линтинг: `flake8`

## Процесс изменений
- Ветка на фичу/фикс.
- Тесты и линтеры обязательны перед merge.
- Обновление `CHANGELOG.md` для релизных изменений.
