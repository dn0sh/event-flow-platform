import pytest

from src.services.nats_service import NatsService


@pytest.mark.asyncio
async def test_nats_mock_fixture(fake_nats):
    conn = await fake_nats.connect()
    assert conn == "nats-connection"


def test_nats_service_class_exists():
    assert NatsService is not None
