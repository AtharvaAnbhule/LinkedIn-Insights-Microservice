import json
from typing import Any
from redis import asyncio as aioredis
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class Cache:
   

    def __init__(self):
        self.redis: aioredis.Redis | None = None

    async def connect(self):

        try:
            self.redis = await aioredis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                encoding="utf-8",
                decode_responses=True
            )

       
            await self.redis.ping()

            logger.info("Connected to Redis successfully")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self):
  
        if self.redis:
            await self.redis.close()
            logger.info("Disconnected from Redis")

    async def ping(self) -> bool:
       
        try:
            if self.redis:
                await self.redis.ping()
                return True
        except Exception:
            pass
        return False

    async def get(self, key: str) -> Any | None:
       
        try:
            if not self.redis:
                return None

            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None

        except Exception as e:
            logger.error(f"Cache get error for key '{key}': {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
       
        try:
            if not self.redis:
                return False

            ttl = ttl or settings.CACHE_TTL
            serialized_value = json.dumps(value, default=str)
            await self.redis.setex(key, ttl, serialized_value)
            return True

        except Exception as e:
            logger.error(f"Cache set error for key '{key}': {e}")
            return False

    async def delete(self, key: str) -> bool:
      
        try:
            if not self.redis:
                return False

            await self.redis.delete(key)
            return True

        except Exception as e:
            logger.error(f"Cache delete error for key '{key}': {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
      
        try:
            if not self.redis:
                return 0

            keys = await self.redis.keys(pattern)
            if keys:
                return await self.redis.delete(*keys)
            return 0

        except Exception as e:
            logger.error(f"Cache clear pattern error for pattern '{pattern}': {e}")
            return 0


cache = Cache()
