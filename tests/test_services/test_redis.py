import pytest

from src.services.redis_service import RedisService


@pytest.mark.asyncio
async def test_redis_jwt_blacklist(fake_redis):
    await fake_redis.blacklist_jwt("jti-1", 100)
    assert await fake_redis.is_jwt_blacklisted("jti-1")


def test_redis_service_class_exists():
    assert RedisService is not None
