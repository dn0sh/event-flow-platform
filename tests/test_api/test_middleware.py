import pytest
from fastapi import Request, Response

from src.api.middleware.rate_limiter import RateLimitMiddleware


@pytest.mark.asyncio
async def test_rate_limiter_allows_health_path():
    middleware = RateLimitMiddleware(app=lambda scope, receive, send: None)
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/health",
        "headers": [],
        "client": ("127.0.0.1", 1234),
        "query_string": b"",
        "server": ("test", 80),
        "scheme": "http",
    }
    request = Request(scope)

    async def call_next(_request):
        return Response(status_code=200)

    response = await middleware.dispatch(request, call_next)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_rate_limiter_skipped_when_limit_zero(monkeypatch):
    import src.api.middleware.rate_limiter as rl

    monkeypatch.setattr(rl.settings, "rate_limit_per_minute", 0)
    middleware = RateLimitMiddleware(app=lambda scope, receive, send: None)
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/orders",
        "headers": [],
        "client": ("127.0.0.1", 1234),
        "query_string": b"",
        "server": ("test", 80),
        "scheme": "http",
    }
    request = Request(scope)

    async def call_next(_request):
        return Response(status_code=200)

    response = await middleware.dispatch(request, call_next)
    assert response.status_code == 200
