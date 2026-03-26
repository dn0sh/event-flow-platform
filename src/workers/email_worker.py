import asyncio

from structlog import get_logger

from src.config.settings import get_settings
from src.services.rabbitmq_service import RabbitMQService
from src.workers.consumer_runner import run_rabbitmq_consumer

logger = get_logger(__name__)


async def _process_email(payload: dict[str, object]) -> None:
    logger.info("email_worker_send", payload=payload)


async def run() -> None:
    settings = get_settings()
    queue = settings.rabbitmq_consumer_queue or RabbitMQService.NOTIFICATIONS_EMAIL
    await run_rabbitmq_consumer(queue, _process_email, health_port=8091, worker_name="email-worker")


if __name__ == "__main__":
    asyncio.run(run())
