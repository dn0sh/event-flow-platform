from fastapi import APIRouter

from src.utils.health import check_redis

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health() -> dict[str, object]:
    redis_ok = await check_redis()
    status = "ok" if redis_ok else "degraded"
    return {
        "status": status,
        "services": {
            "redis": "up" if redis_ok else "down",
        },
    }
