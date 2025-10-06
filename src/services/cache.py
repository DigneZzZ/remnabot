"""
Cache service module using Redis
"""
import json
from typing import Optional, Any
from datetime import timedelta
import redis.asyncio as aioredis
from src.core.config import settings
from src.core.logger import log


class CacheService:
    """
    Redis cache service for storing temporary data
    """
    
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self.enabled = settings.redis_enabled
        
    async def connect(self):
        """Connect to Redis"""
        if not self.enabled:
            log.info("Redis caching is disabled")
            return
        
        try:
            self.redis = await aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis.ping()
            log.info("Successfully connected to Redis")
        except Exception as e:
            log.error(f"Failed to connect to Redis: {e}")
            self.enabled = False
            self.redis = None
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
            log.info("Disconnected from Redis")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled or not self.redis:
            return None
        
        try:
            value = await self.redis.get(key)
            if value:
                log.debug(f"Cache hit: {key}")
                return json.loads(value)
            log.debug(f"Cache miss: {key}")
            return None
        except Exception as e:
            log.error(f"Error getting from cache: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[timedelta] = None
    ):
        """Set value in cache"""
        if not self.enabled or not self.redis:
            return
        
        try:
            serialized = json.dumps(value)
            if expire:
                await self.redis.setex(key, expire, serialized)
            else:
                await self.redis.set(key, serialized)
            log.debug(f"Cache set: {key}")
        except Exception as e:
            log.error(f"Error setting cache: {e}")
    
    async def delete(self, key: str):
        """Delete value from cache"""
        if not self.enabled or not self.redis:
            return
        
        try:
            await self.redis.delete(key)
            log.debug(f"Cache deleted: {key}")
        except Exception as e:
            log.error(f"Error deleting from cache: {e}")
    
    async def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern"""
        if not self.enabled or not self.redis:
            return
        
        try:
            keys = []
            async for key in self.redis.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                await self.redis.delete(*keys)
                log.debug(f"Cleared {len(keys)} keys matching pattern: {pattern}")
        except Exception as e:
            log.error(f"Error clearing cache pattern: {e}")


# Create global cache service instance
cache_service = CacheService()
