from src.services.redis_service import redis_service


async def check_redis() -> bool:
    try:
        return await redis_service.ping()
    except Exception:
        return False
