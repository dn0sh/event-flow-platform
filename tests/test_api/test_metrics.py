import pytest


@pytest.mark.asyncio
async def test_metrics_endpoint_exposes_prometheus_text(client):
    """Instrumentator and app metrics must be registered on /metrics."""
    await client.get("/health")
    response = await client.get("/metrics")
    assert response.status_code == 200
    body = response.text
    assert "http_request_duration_seconds" in body
    assert "http_requests_total" in body
    assert "orders_created_total" in body
