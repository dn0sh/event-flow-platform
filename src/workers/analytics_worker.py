import asyncio

from structlog import get_logger

from src.config.settings import get_settings
from src.services.kafka_service import KafkaService
from src.workers.consumer_runner import run_kafka_consumer

logger = get_logger(__name__)


async def _process_analytics(payload: dict[str, object]) -> None:
    logger.info("analytics_worker_event", payload=payload)


async def run() -> None:
    settings = get_settings()
    topic = settings.kafka_consumer_topic or KafkaService.ORDER_EVENTS_TOPIC
    group = settings.kafka_consumer_group or KafkaService.ANALYTICS_GROUP
    await run_kafka_consumer(
        topic,
        group,
        _process_analytics,
        health_port=8094,
        worker_name="analytics-worker",
    )


if __name__ == "__main__":
    asyncio.run(run())
