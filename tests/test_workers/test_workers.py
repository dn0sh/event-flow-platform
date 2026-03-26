import pytest

from src.workers import analytics_worker, email_worker, logger_worker, telegram_worker


@pytest.mark.asyncio
async def test_workers_run_entrypoints(monkeypatch):
    called = {"email": 0, "logger": 0, "analytics": 0, "telegram": 0}

    async def _run_email():
        called["email"] += 1

    async def _run_logger():
        called["logger"] += 1

    async def _run_analytics():
        called["analytics"] += 1

    async def _run_telegram():
        called["telegram"] += 1

    monkeypatch.setattr(email_worker, "run", _run_email)
    monkeypatch.setattr(logger_worker, "run", _run_logger)
    monkeypatch.setattr(analytics_worker, "run", _run_analytics)
    monkeypatch.setattr(telegram_worker, "run", _run_telegram)

    await email_worker.run()
    await logger_worker.run()
    await analytics_worker.run()
    await telegram_worker.run()

    assert called == {"email": 1, "logger": 1, "analytics": 1, "telegram": 1}
