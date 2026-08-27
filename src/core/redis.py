from typing import Optional
import redis.asyncio as aioredis
from redis.asyncio import Redis

from src.core.config import settings

redis_client: Optional[Redis] = None

async def init_redis_pool() -> None:
    global redis_client
    redis_client = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )
    await redis_client.ping()

async def close_redis_pool() -> None:
    global redis_client
    if redis_client:
        await redis_client.close()

def get_redis() -> Redis:
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized. Check lifespan startup")
    return redis_client