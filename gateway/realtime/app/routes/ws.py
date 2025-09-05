import os
import asyncio
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from redis.asyncio import Redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
ROOM_PREFIX = "room:"

redis = Redis.from_url(REDIS_URL, decode_responses=True)

sub_tasks: Dict[str, asyncio.Task] = {}
rooms: Dict[str, Set[WebSocket]] = {}

router = APIRouter()


async def ensure_room_subscription(session_id: str):
    if session_id in sub_tasks:
        return

    async def reader():
        pubsub = redis.pubsub()
        channel = ROOM_PREFIX + session_id
        await pubsub.subscribe(channel)
        async for msg in pubsub.listen():
            if msg.get("type") == "message":
                payload = msg.get("data")
                for ws in list(rooms.get(session_id, set())):
                    try:
                        await ws.send_text(payload)
                    except Exception:
                        try:
                            await ws.close()
                        except Exception:
                            pass
                        rooms[session_id].discard(ws)

    sub_tasks[session_id] = asyncio.create_task(reader())


@router.websocket("/ws/{session_id}")
async def ws_session(websocket: WebSocket, session_id: str):
    await websocket.accept()
    rooms.setdefault(session_id, set()).add(websocket)
    await ensure_room_subscription(session_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        rooms.get(session_id, set()).discard(websocket)
