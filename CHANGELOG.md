# Changelog

Все значимые изменения фиксируются в этом файле. Формат основан на [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), версия проекта — [SemVer](https://semver.org/).

## [Unreleased]

## [1.1.0] - 2026-03-26

### Added

- FastAPI `lifespan` for startup/shutdown; NATS bridge returns `NatsBridgeResources` with graceful `drain`/`close` on shutdown (ADR 005).
- RabbitMQ/Kafka consumer loops in `src/workers/consumer_runner.py` with env-driven queue/topic/group (ADR 006).
- Docker Compose: API healthcheck via `python` + `urllib` (no `curl` in slim image); split workers `worker-email`, `worker-telegram`, `worker-analytics`, `worker-logger`.
- Grafana dashboards: PromQL for `http_request_duration_seconds`, `http_requests_total`, `orders_created_total`, `error_rate_total`, `queue_depth`, HTTP 5xx ratio; Prometheus datasource `uid: prometheus`; explicit `metrics_path: /metrics` for API scrape.
- Tests: `/metrics` content check; NATS `stop_nats_bridge` / successful bridge start; `conftest` async fixtures typed with `AsyncIterator` / `AsyncGenerator`.
- `.bandit` config skipping `B104` for intentional `0.0.0.0` binds in containers.
- Coverage: `omit` for `consumer_runner.py` (integration path); `fail_under` 85% in `[tool.coverage.report]`.
- ADR 005 (lifespan), ADR 006 (worker consumption).

### Changed

- Redis `ping()` uses `await` on async client (mypy-friendly `cast`).
- README / `.env.example`: production warnings for `JWT_SECRET`.
- `pyproject.toml` / `.version/VERSION` / OpenAPI app version set to **1.1.0**.

### Fixed

- Docker API healthcheck no longer depends on missing `curl` in `Dockerfile.api`.

### Security

- **Known:** `safety` may report `ecdsa` (transitive via `python-jose`) side-channel findings; pure-Python limitation; track upstream advisories.

## [1.0.0] - 2026-03-26

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

- Initial release fixes (see git history)
