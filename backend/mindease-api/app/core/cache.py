"""
Redis Cache Utilities for MindEase API

This module provides comprehensive caching functionality using Redis
for session management, API response caching, and performance optimization.
"""

import json
import pickle
import logging
from typing import Any, Optional, Union, Dict, List
from datetime import datetime, timedelta
from functools import wraps

import redis.asyncio as redis
from redis.asyncio import Redis
from fastapi import Request

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Global Redis client instance
_redis_client: Optional[Redis] = None


async def get_redis_client() -> Redis:
    """
    Get Redis client instance with connection pooling.
    
    Returns:
        Redis client instance
    """
    global _redis_client
    
    if _redis_client is None:
        try:
            _redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20,
                retry_on_timeout=True,
                socket_keepalive=True,
                socket_keepalive_options={},
                health_check_interval=30
            )
            
            # Test connection
            await _redis_client.ping()
            logger.info("Redis connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise
    
    return _redis_client


async def close_redis_client() -> None:
    """Close Redis client connection."""
    global _redis_client
    
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis connection closed")


class CacheManager:
    """Redis cache manager with advanced features."""
    
    def __init__(self, redis_client: Optional[Redis] = None):
        self.redis_client = redis_client
        
    async def get_client(self) -> Redis:
        """Get Redis client instance."""
        if not self.redis_client:
            self.redis_client = await get_redis_client()
        return self.redis_client
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None,
        namespace: Optional[str] = None
    ) -> bool:
        """
        Set a value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            expire: Expiration time in seconds
            namespace: Optional namespace prefix
            
        Returns:
            True if successful, False otherwise
        """
        try:
            client = await self.get_client()
            
            # Add namespace prefix
            if namespace:
                key = f"{namespace}:{key}"
            
            # Serialize value
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value, default=str)
            elif isinstance(value, (str, int, float, bool)):
                serialized_value = str(value)
            else:
                # Use pickle for complex objects
                serialized_value = pickle.dumps(value).hex()
                key = f"pickle:{key}"
            
            # Set value with optional expiration
            if expire:
                await client.setex(key, expire, serialized_value)
            else:
                await client.set(key, serialized_value)
            
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {str(e)}")
            return False
    
    async def get(
        self,
        key: str,
        namespace: Optional[str] = None,
        default: Any = None
    ) -> Any:
        """
        Get a value from cache.
        
        Args:
            key: Cache key
            namespace: Optional namespace prefix
            default: Default value if key not found
            
        Returns:
            Cached value or default
        """
        try:
            client = await self.get_client()
            
            # Add namespace prefix
            if namespace:
                key = f"{namespace}:{key}"
            
            value = await client.get(key)
            
            if value is None:
                return default
            
            # Deserialize value
            if key.startswith("pickle:"):
                return pickle.loads(bytes.fromhex(value))
            
            # Try JSON deserialization first
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # Return as string if not JSON
                return value
                
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {str(e)}")
            return default
    
    async def delete(self, key: str, namespace: Optional[str] = None) -> bool:
        """
        Delete a key from cache.
        
        Args:
            key: Cache key
            namespace: Optional namespace prefix
            
        Returns:
            True if successful, False otherwise
        """
        try:
            client = await self.get_client()
            
            if namespace:
                key = f"{namespace}:{key}"
            
            result = await client.delete(key)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {str(e)}")
            return False
    
    async def exists(self, key: str, namespace: Optional[str] = None) -> bool:
        """
        Check if a key exists in cache.
        
        Args:
            key: Cache key
            namespace: Optional namespace prefix
            
        Returns:
            True if key exists, False otherwise
        """
        try:
            client = await self.get_client()
            
            if namespace:
                key = f"{namespace}:{key}"
            
            result = await client.exists(key)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {str(e)}")
            return False
    
    async def expire(self, key: str, seconds: int, namespace: Optional[str] = None) -> bool:
        """
        Set expiration for a key.
        
        Args:
            key: Cache key
            seconds: Expiration time in seconds
            namespace: Optional namespace prefix
            
        Returns:
            True if successful, False otherwise
        """
        try:
            client = await self.get_client()
            
            if namespace:
                key = f"{namespace}:{key}"
            
            result = await client.expire(key, seconds)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Cache expire error for key {key}: {str(e)}")
            return False
    
    async def increment(
        self,
        key: str,
        amount: int = 1,
        namespace: Optional[str] = None,
        expire: Optional[int] = None
    ) -> Optional[int]:
        """
        Increment a numeric value in cache.
        
        Args:
            key: Cache key
            amount: Amount to increment
            namespace: Optional namespace prefix
            expire: Optional expiration time
            
        Returns:
            New value after increment, None if error
        """
        try:
            client = await self.get_client()
            
            if namespace:
                key = f"{namespace}:{key}"
            
            # Use pipeline for atomic operation
            pipe = client.pipeline()
            pipe.incrby(key, amount)
            
            if expire:
                pipe.expire(key, expire)
            
            results = await pipe.execute()
            return results[0]
            
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {str(e)}")
            return None
    
    async def get_keys(self, pattern: str, namespace: Optional[str] = None) -> List[str]:
        """
        Get keys matching a pattern.
        
        Args:
            pattern: Key pattern (supports wildcards)
            namespace: Optional namespace prefix
            
        Returns:
            List of matching keys
        """
        try:
            client = await self.get_client()
            
            if namespace:
                pattern = f"{namespace}:{pattern}"
            
            keys = await client.keys(pattern)
            
            # Remove namespace prefix from results
            if namespace:
                prefix_len = len(namespace) + 1
                keys = [key[prefix_len:] for key in keys if key.startswith(f"{namespace}:")]
            
            return keys
            
        except Exception as e:
            logger.error(f"Cache get_keys error for pattern {pattern}: {str(e)}")
            return []
    
    async def clear_namespace(self, namespace: str) -> int:
        """
        Clear all keys in a namespace.
        
        Args:
            namespace: Namespace to clear
            
        Returns:
            Number of keys deleted
        """
        try:
            client = await self.get_client()
            
            keys = await client.keys(f"{namespace}:*")
            
            if keys:
                deleted = await client.delete(*keys)
                return deleted
            
            return 0
            
        except Exception as e:
            logger.error(f"Cache clear_namespace error for {namespace}: {str(e)}")
            return 0


# Global cache manager instance
cache_manager = CacheManager()


class SessionCache:
    """Session management using Redis."""
    
    SESSION_NAMESPACE = "session"
    DEFAULT_EXPIRE = 3600 * 24 * 7  # 7 days
    
    @staticmethod
    async def create_session(user_id: int, session_data: Dict[str, Any]) -> str:
        """
        Create a new user session.
        
        Args:
            user_id: User ID
            session_data: Session data to store
            
        Returns:
            Session ID
        """
        import uuid
        
        session_id = str(uuid.uuid4())
        session_key = f"user:{user_id}:session:{session_id}"
        
        # Add metadata
        session_data.update({
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_accessed": datetime.utcnow().isoformat()
        })
        
        success = await cache_manager.set(
            key=session_key,
            value=session_data,
            expire=SessionCache.DEFAULT_EXPIRE,
            namespace=SessionCache.SESSION_NAMESPACE
        )
        
        if success:
            return session_id
        else:
            raise Exception("Failed to create session")
    
    @staticmethod
    async def get_session(user_id: int, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data.
        
        Args:
            user_id: User ID
            session_id: Session ID
            
        Returns:
            Session data or None
        """
        session_key = f"user:{user_id}:session:{session_id}"
        
        session_data = await cache_manager.get(
            key=session_key,
            namespace=SessionCache.SESSION_NAMESPACE
        )
        
        if session_data:
            # Update last accessed time
            session_data["last_accessed"] = datetime.utcnow().isoformat()
            await cache_manager.set(
                key=session_key,
                value=session_data,
                expire=SessionCache.DEFAULT_EXPIRE,
                namespace=SessionCache.SESSION_NAMESPACE
            )
        
        return session_data
    
    @staticmethod
    async def delete_session(user_id: int, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            user_id: User ID
            session_id: Session ID
            
        Returns:
            True if successful
        """
        session_key = f"user:{user_id}:session:{session_id}"
        
        return await cache_manager.delete(
            key=session_key,
            namespace=SessionCache.SESSION_NAMESPACE
        )
    
    @staticmethod
    async def delete_user_sessions(user_id: int) -> int:
        """
        Delete all sessions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of sessions deleted
        """
        pattern = f"user:{user_id}:session:*"
        keys = await cache_manager.get_keys(
            pattern=pattern,
            namespace=SessionCache.SESSION_NAMESPACE
        )
        
        deleted = 0
        for key in keys:
            if await cache_manager.delete(key, SessionCache.SESSION_NAMESPACE):
                deleted += 1
        
        return deleted


def cache_response(expire: int = 300, namespace: str = "api_response"):
    """
    Decorator for caching API responses.
    
    Args:
        expire: Cache expiration time in seconds
        namespace: Cache namespace
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get cached response
            cached_response = await cache_manager.get(
                key=cache_key,
                namespace=namespace
            )
            
            if cached_response is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_response
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            
            await cache_manager.set(
                key=cache_key,
                value=result,
                expire=expire,
                namespace=namespace
            )
            
            logger.debug(f"Cache miss for {cache_key}, result cached")
            return result
        
        return wrapper
    return decorator


async def get_cache_stats() -> Dict[str, Any]:
    """
    Get Redis cache statistics.
    
    Returns:
        Dictionary containing cache statistics
    """
    try:
        client = await get_redis_client()
        info = await client.info()
        
        return {
            "redis_version": info.get("redis_version"),
            "connected_clients": info.get("connected_clients"),
            "used_memory": info.get("used_memory"),
            "used_memory_human": info.get("used_memory_human"),
            "total_commands_processed": info.get("total_commands_processed"),
            "keyspace_hits": info.get("keyspace_hits"),
            "keyspace_misses": info.get("keyspace_misses"),
            "hit_rate": (
                info.get("keyspace_hits", 0) / 
                max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1)
            ) * 100
        }
        
    except Exception as e:
        logger.error(f"Failed to get cache stats: {str(e)}")
        return {"error": "Failed to retrieve cache statistics"}


# Export main components
__all__ = [
    "get_redis_client",
    "close_redis_client",
    "CacheManager",
    "cache_manager",
    "SessionCache",
    "cache_response",
    "get_cache_stats"
]

