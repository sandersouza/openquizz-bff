import os
from redis.asyncio import Redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis = Redis.from_url(REDIS_URL, decode_responses=True)

ROOM_PREFIX = "room:"
PIN_PREFIX = "pin:"

async def publish(room: str, event: dict):
    await redis.publish(ROOM_PREFIX + room, str(event))
