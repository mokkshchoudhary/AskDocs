from fastapi import HTTPException, Request, Depends
from app.core.config import settings
import redis.asyncio as redis
from app.core import logging

logger = logging.logger

async def get_redis_client():
    client = redis.from_url(settings.REDIS_URI, encoding="utf-8", decode_responses=True)
    try:
        yield client
    finally:
        await client.close()

class RateLimiter:
    def __init__(self, times: int = 10, seconds: int = 60):
        self.times = times
        self.seconds = seconds

    async def __call__(self, request: Request, client: redis.Redis = Depends(get_redis_client)):
        # Identify user by IP or User ID if authenticated
        # For authenticated endpoints, we could use user_id, but this runs before auth deps often?
        # Actually dependency runs in order. 
        # If we use it as a dependency in the router, it executes.
        # Let's simple use client.host for now as fallback, or Auth Header.
        
        # Simple IP based key
        key = f"rate_limit:{request.client.host}"
        
        # Increment
        count = await client.incr(key)
        
        # If first time, set expire
        if count == 1:
            await client.expire(key, self.seconds)
            
        if count > self.times:
            raise HTTPException(status_code=429, detail="Too many requests")

# Expose a default instance
limiter = RateLimiter(times=20, seconds=60)
