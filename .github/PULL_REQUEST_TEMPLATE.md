## Изменения
- [ ] Описал цель и мотивацию изменений
- [ ] Обновил документацию (если нужно)
- [ ] Обновил `CHANGELOG.md` (если нужно)

## Проверки качества
- [ ] `black --check .`
- [ ] `isort --check-only .`
- [ ] `flake8 src tests`
- [ ] `mypy src`
- [ ] `pytest --cov=src --cov-fail-under=85`
- [ ] `bandit -r src`
- [ ] `safety check --full-report`

## Брокеры и интеграции
- [ ] Проверил Redis/RabbitMQ/Kafka/NATS сценарии (если затронуто)
- [ ] Для WebSocket проверил auth + heartbeat + room subscribe
- [ ] Для Bot проверил команды и admin restrictions

## Деплой и риски
- [ ] Изменения обратимы
- [ ] Описал риски и rollback-план
