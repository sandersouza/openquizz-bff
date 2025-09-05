from fastapi import APIRouter
from .ws import redis

router = APIRouter()


@router.get("/healthz")
async def health():
    pong = await redis.ping()
    return {"status": "ok", "redis": pong}
