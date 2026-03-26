import pytest

from src.services import kafka_service, nats_service, rabbitmq_service, redis_service


class FakePipeline:
    def __init__(self):
        self._count = 0

    def zremrangebyscore(self, *_args):
        return self

    def zadd(self, *_args, **_kwargs):
        return self

    def zcard(self, *_args):
        return self

    def expire(self, *_args):
        return self

    async def execute(self):
        return [None, None, self._count, True]


class FakeRedisClient:
    def __init__(self):
        self.values = {}
        self.pipeline_obj = FakePipeline()

    async def ping(self):
        return True

    async def get(self, key):
        return self.values.get(key)

    async def setex(self, key, _ttl, value):
        self.values[key] = value

    async def delete(self, key):
        self.values.pop(key, None)

    async def exists(self, key):
        return 1 if key in self.values else 0

    def pipeline(self):
        return self.pipeline_obj


@pytest.mark.asyncio
async def test_redis_service_methods():
    svc = redis_service.RedisService()
    svc._client = FakeRedisClient()
    assert await svc.ping()
    await svc.set_cached_order("1", "x")
    assert await svc.get_cached_order("1") == "x"
    await svc.invalidate_order("1")
    await svc.blacklist_jwt("j1", 10)
    assert await svc.is_jwt_blacklisted("j1")
    assert await svc.is_rate_limited("127.0.0.1", 100) is False


@pytest.mark.asyncio
async def test_rabbitmq_connect(monkeypatch):
    captured = {}

    async def fake_connect_robust(**kwargs):
        captured.update(kwargs)
        return "ok"

    monkeypatch.setattr(rabbitmq_service.aio_pika, "connect_robust", fake_connect_robust)
    svc = rabbitmq_service.RabbitMQService()
    result = await svc.connect()
    assert result == "ok"
    assert captured["host"]


@pytest.mark.asyncio
async def test_kafka_builders(monkeypatch):
    class FakeProducer:
        async def start(self):
            return None

        async def send_and_wait(self, _topic, _payload):
            return None

    class FakeConsumer:
        async def start(self):
            return None

    class FakeClient:
        status_code = 200

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def post(self, *_args, **_kwargs):
            return self

        def raise_for_status(self):
            return None

        def json(self):
            return {"id": 1}

    monkeypatch.setattr(kafka_service, "AIOKafkaProducer", lambda **_kwargs: FakeProducer())
    monkeypatch.setattr(
        kafka_service, "AIOKafkaConsumer", lambda *_args, **_kwargs: FakeConsumer()
    )
    monkeypatch.setattr(kafka_service.httpx, "AsyncClient", lambda timeout: FakeClient())
    svc = kafka_service.KafkaService()
    producer = await svc.build_producer()
    consumer = await svc.build_consumer("order.events", "analytics-consumer")
    await svc.publish_order_event(producer, {"event": "created"})
    await svc.publish_audit_log(producer, {"audit": "ok"})
    schema = await svc.register_schema("order.events-value", {"type": "record"})
    assert producer is not None
    assert consumer is not None
    assert schema["id"] == 1


@pytest.mark.asyncio
async def test_nats_connect(monkeypatch):
    class FakeNatsClient:
        def __init__(self):
            self.sent = []

        async def connect(self, _url):
            return None

        def jetstream(self):
            return "jetstream"

        async def publish(self, subject, payload):
            self.sent.append((subject, payload))

    monkeypatch.setattr(nats_service, "NATS", FakeNatsClient)
    svc = nats_service.NatsService()
    client = await svc.connect()
    await svc.publish_realtime(client, b"a")
    await svc.publish_presence(client, b"b")
    await svc.publish_health(client, b"c")
    stream = await svc.get_stream(client)
    assert client is not None
    assert stream in ("jetstream", None)
