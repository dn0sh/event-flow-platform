from __future__ import annotations

import time
from collections.abc import Sequence
from typing import Any, Awaitable, cast

from redis.asyncio import Redis

from src.config.settings import get_settings

settings = get_settings()


class RedisService:
    def __init__(self) -> None:
        self._client = Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
        )

    async def ping(self) -> bool:
        raw = self._client.ping()
        return bool(await cast(Awaitable[bool], raw))

    async def get_cached_order(self, order_id: str) -> str | None:
        value = await self._client.get(f"order:{order_id}")
        return cast(str | None, value)

    async def set_cached_order(self, order_id: str, payload: str) -> None:
        await self._client.setex(f"order:{order_id}", settings.redis_ttl_seconds, payload)

    async def invalidate_order(self, order_id: str) -> None:
        await self._client.delete(f"order:{order_id}")

    async def blacklist_jwt(self, jti: str, ttl_seconds: int) -> None:
        await self._client.setex(f"jwt:blacklist:{jti}", ttl_seconds, "1")

    async def is_jwt_blacklisted(self, jti: str) -> bool:
        return bool(await self._client.exists(f"jwt:blacklist:{jti}"))

    async def is_rate_limited(self, ip_address: str, limit: int) -> bool:
        now = int(time.time() * 1000)
        key = f"ratelimit:{ip_address}"
        window_ms = 60_000
        pipe = self._client.pipeline()
        min_score = now - window_ms
        pipe.zremrangebyscore(key, 0, min_score)
        pipe.zadd(key, {str(now): now})
        pipe.zcard(key)
        pipe.expire(key, 61)
        result: Sequence[Any] = await pipe.execute()
        count_value = result[2] if len(result) > 2 else 0
        current_count = int(count_value) if isinstance(count_value, (int, float, str)) else 0
        return current_count > limit


redis_service = RedisService()
