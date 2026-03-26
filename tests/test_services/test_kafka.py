import pytest

from src.services.kafka_service import KafkaService


@pytest.mark.asyncio
async def test_kafka_mock_fixture(fake_kafka):
    producer = await fake_kafka.build_producer()
    consumer = await fake_kafka.build_consumer("order.events", "analytics-consumer")
    assert producer == "kafka-producer"
    assert consumer.endswith("analytics-consumer")


def test_kafka_service_class_exists():
    assert KafkaService is not None
