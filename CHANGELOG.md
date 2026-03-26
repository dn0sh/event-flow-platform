# Changelog

Все значимые изменения фиксируются в этом файле. Формат основан на [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), версия проекта — [SemVer](https://semver.org/).

## [Unreleased]
### Added
- Telegram Bot production handlers: `/start`, `/orders`, `/subscribe`, `/status`, `/help`
- Inline keyboard actions for order view/status/cancel
- RabbitMQ enqueue integration for bot notifications and callbacks
- Admin access restriction by `TELEGRAM_ADMIN_IDS`
- Bot graceful shutdown with signal handling and structlog events
- JWT-protected WebSocket endpoint `/ws/notifications` with room subscribe/unsubscribe
- WebSocket heartbeat contract (`ping`/`pong`) and NATS realtime bridge bootstrap
- WebSocket client reconnect contract documentation in `docs/api/websocket.md`
- Worker runtime orchestration with signal-based lifecycle and health endpoints
- Worker retry/backoff, circuit breaker guard, and idempotency by message id
- Docker healthchecks for `bot` and `worker` services
- GitHub issue templates for bug report and feature request
- Pull request template with CI quality checklist
- Locust load-test scenarios for create orders, cache-biased reads, and status updates
- Automatic load-test summary export to `results/locust_summary.json` and `results/benchmark_report.md`
- Broker comparison benchmark generator in `scripts/benchmark.py`
- Extended architecture and development docs for faster onboarding
- Detailed API curl examples and WebSocket contract docs
- Expanded ADR 001-004 with context/decision/consequences/alternatives
- README quickstart for Linux/Windows and troubleshooting section
- Updated ROADMAP with additional Q2/Q3 milestones

### Changed
- CI workflow split into lint/type-check/test/security/build jobs with pip cache and Docker layer cache
- Docker images now build and push to GHCR on pushes to `main`
- CD workflow deploys to staging on `main`, runs health checks, sends Telegram notifications, and performs rollback on failure

### Fixed

## [1.0.0] - 2026-03-26
### Added
- Initial release
- Redis caching
- RabbitMQ queues
- Kafka event streaming
- NATS pub/sub
- Telegram Bot
- REST API
- WebSocket notifications
