import pytest
from httpx import ASGITransport, AsyncClient

from src.api.main import app
from src.services.postgres_service import get_db_session


class FakeRedis:
    def __init__(self) -> None:
        self.cache: dict[str, str] = {}
        self.blacklist: set[str] = set()

    async def ping(self) -> bool:
        return True

    async def get_cached_order(self, order_id: str) -> str | None:
        return self.cache.get(order_id)

    async def set_cached_order(self, order_id: str, payload: str) -> None:
        self.cache[order_id] = payload

    async def invalidate_order(self, order_id: str) -> None:
        self.cache.pop(order_id, None)

    async def blacklist_jwt(self, jti: str, ttl_seconds: int) -> None:
        self.blacklist.add(jti)

    async def is_jwt_blacklisted(self, jti: str) -> bool:
        return jti in self.blacklist

    async def is_rate_limited(self, ip_address: str, limit: int) -> bool:
        return False


class FakeRabbitMQ:
    async def connect(self) -> str:
        return "rabbitmq-connection"


class FakeKafka:
    async def build_producer(self) -> str:
        return "kafka-producer"

    async def build_consumer(self, topic: str, group_id: str) -> str:
        return f"kafka-consumer:{topic}:{group_id}"


class FakeNats:
    async def connect(self) -> str:
        return "nats-connection"


@pytest.fixture()
def fake_redis() -> FakeRedis:
    return FakeRedis()


@pytest.fixture()
def fake_rabbitmq() -> FakeRabbitMQ:
    return FakeRabbitMQ()


@pytest.fixture()
def fake_kafka() -> FakeKafka:
    return FakeKafka()


@pytest.fixture()
def fake_nats() -> FakeNats:
    return FakeNats()


@pytest.fixture()
async def client() -> AsyncClient:
    async def _no_db():
        yield None

    app.dependency_overrides[get_db_session] = _no_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
