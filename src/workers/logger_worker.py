import asyncio

from structlog import get_logger

from src.config.settings import get_settings
from src.services.kafka_service import KafkaService
from src.workers.consumer_runner import run_kafka_consumer

logger = get_logger(__name__)


async def _process_log(payload: dict[str, object]) -> None:
    logger.info("logger_worker_event", payload=payload)


async def run() -> None:
    settings = get_settings()
    topic = settings.kafka_consumer_topic or KafkaService.AUDIT_LOG_TOPIC
    group = settings.kafka_consumer_group or KafkaService.LOGGER_GROUP
    await run_kafka_consumer(
        topic, group, _process_log, health_port=8093, worker_name="logger-worker"
    )


if __name__ == "__main__":
    asyncio.run(run())
