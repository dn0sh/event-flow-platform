from nats.aio.client import Client as NATS
from nats.js import JetStreamContext
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config.settings import get_settings

settings = get_settings()


class NatsService:
    REALTIME_SUBJECT = "notifications.realtime"
    PRESENCE_SUBJECT = "presence.online"
    HEALTH_SUBJECT = "system.health"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    async def connect(self) -> NATS:
        client = NATS()
        await client.connect(settings.nats_url)
        return client

    async def get_stream(self, client: NATS) -> JetStreamContext | None:
        if not settings.nats_use_jetstream:
            return None
        return client.jetstream()

    async def publish_realtime(self, client: NATS, payload: bytes) -> None:
        await client.publish(self.REALTIME_SUBJECT, payload)

    async def publish_presence(self, client: NATS, payload: bytes) -> None:
        await client.publish(self.PRESENCE_SUBJECT, payload)

    async def publish_health(self, client: NATS, payload: bytes) -> None:
        await client.publish(self.HEALTH_SUBJECT, payload)
