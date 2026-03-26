import pytest

from src.services.rabbitmq_service import RabbitMQService


@pytest.mark.asyncio
async def test_rabbitmq_mock_fixture(fake_rabbitmq):
    conn = await fake_rabbitmq.connect()
    assert conn == "rabbitmq-connection"


def test_rabbitmq_service_class_exists():
    assert RabbitMQService is not None


@pytest.mark.asyncio
async def test_rabbitmq_topology_and_publish():
    class FakeExchange:
        def __init__(self, name):
            self.name = name

        async def publish(self, _message, routing_key):
            return None

    class FakeChannel:
        def __init__(self):
            self.default_exchange = FakeExchange("default")

        async def declare_exchange(self, name, _type, durable=True):
            return FakeExchange(name)

        async def declare_queue(self, _name, durable=True, arguments=None):
            return None

    svc = RabbitMQService()
    channel = FakeChannel()
    await svc.setup_topology(channel)
    await svc.publish_json(channel, svc.ORDERS_PENDING, {"id": "1"}, priority=5)


@pytest.mark.asyncio
async def test_rabbitmq_process_with_retry():
    class Msg:
        def __init__(self):
            self.body = b'{"x":1}'
            self.headers = {"x-retry-count": 0}
            self.acked = False
            self.nacked = False
            self.rejected = False

        async def ack(self):
            self.acked = True

        async def nack(self, requeue=True):
            self.nacked = requeue

        async def reject(self, requeue=False):
            self.rejected = not requeue

    svc = RabbitMQService()
    ok_message = Msg()

    async def good(_payload):
        return None

    await svc.process_with_retry(ok_message, good)
    assert ok_message.acked

    async def failing(_payload):
        raise RuntimeError("err")

    bad_message = Msg()
    await svc.process_with_retry(bad_message, failing)
    assert bad_message.nacked
