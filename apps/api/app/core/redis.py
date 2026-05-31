"""
AxonBridge — Redis Client

Redis connection for session cache, rate limiting, and pub/sub.
"""

import redis.asyncio as redis

from app.core.config import get_settings

settings = get_settings()

# Global Redis connection pool
_redis_pool: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    """Get or create the Redis connection."""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50,
        )
    return _redis_pool


async def check_redis_health() -> bool:
    """Verify Redis connectivity."""
    try:
        client = await get_redis()
        await client.ping()
        return True
    except Exception:
        return False


async def close_redis() -> None:
    """Gracefully close the Redis connection pool."""
    global _redis_pool
    if _redis_pool is not None:
        await _redis_pool.close()
        _redis_pool = None


# ---------- Session Management ----------


async def store_session(
    user_id: str,
    session_id: str,
    data: dict,
    ttl_seconds: int = 1800,
) -> None:
    """Store a user session in Redis."""
    client = await get_redis()
    key = f"session:{user_id}:{session_id}"
    import json
    await client.setex(key, ttl_seconds, json.dumps(data))


async def get_session(user_id: str, session_id: str) -> dict | None:
    """Retrieve a user session from Redis."""
    client = await get_redis()
    key = f"session:{user_id}:{session_id}"
    data = await client.get(key)
    if data:
        import json
        return json.loads(data)
    return None


async def invalidate_session(user_id: str, session_id: str) -> None:
    """Invalidate a specific user session."""
    client = await get_redis()
    key = f"session:{user_id}:{session_id}"
    await client.delete(key)


async def invalidate_all_sessions(user_id: str) -> None:
    """Invalidate all sessions for a user."""
    client = await get_redis()
    pattern = f"session:{user_id}:*"
    keys = []
    async for key in client.scan_iter(match=pattern):
        keys.append(key)
    if keys:
        await client.delete(*keys)


# ---------- Rate Limiting ----------


async def check_rate_limit(
    identifier: str,
    max_requests: int,
    window_seconds: int = 60,
) -> tuple[bool, int]:
    """
    Check rate limit for an identifier.
    Returns (is_allowed, remaining_requests).
    """
    client = await get_redis()
    key = f"ratelimit:{identifier}"

    current = await client.get(key)
    if current is None:
        await client.setex(key, window_seconds, 1)
        return True, max_requests - 1

    current_count = int(current)
    if current_count >= max_requests:
        return False, 0

    await client.incr(key)
    return True, max_requests - current_count - 1


# ---------- Token Blacklist ----------


async def blacklist_token(jti: str, ttl_seconds: int) -> None:
    """Add a token JTI to the blacklist (for logout)."""
    client = await get_redis()
    key = f"token_blacklist:{jti}"
    await client.setex(key, ttl_seconds, "1")


async def is_token_blacklisted(jti: str) -> bool:
    """Check if a token JTI is blacklisted."""
    client = await get_redis()
    key = f"token_blacklist:{jti}"
    return await client.exists(key) > 0
