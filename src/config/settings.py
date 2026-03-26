from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    env: str = "development"
    log_level: str = "INFO"

    api_host: str = "0.0.0.0"
    api_port: int = 8060
    api_base_url: str = "http://api:8060"

    jwt_secret: str = Field(default="change-me", min_length=8)
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "event_system"
    postgres_user: str = "event_user"
    postgres_password: str = "event_password"

    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    redis_ttl_seconds: int = 300
    rate_limit_per_minute: int = 100

    rabbitmq_host: str = "rabbitmq"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"

    kafka_bootstrap_servers: str = "kafka:9092"
    schema_registry_url: str = "http://schema-registry:8081"

    nats_url: str = "nats://nats:4222"
    nats_use_jetstream: bool = False

    telegram_bot_token: str = "your_telegram_bot_token"
    telegram_admin_ids: str = ""

    rabbitmq_consumer_queue: str = ""
    kafka_consumer_topic: str = ""
    kafka_consumer_group: str = ""

    @property
    def telegram_admin_id_set(self) -> set[int]:
        values = [item.strip() for item in self.telegram_admin_ids.split(",") if item.strip()]
        return {int(v) for v in values if v.isdigit()}

    @property
    def sqlalchemy_dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
