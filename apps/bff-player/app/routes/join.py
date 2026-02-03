import os
import httpx
from fastapi import APIRouter, HTTPException
from common_schemas import JoinRequest

UPSTREAM_GAME = os.getenv("UPSTREAM_GAME", "http://game-service:8000")

router = APIRouter()

@router.post("/player/join")
async def join(req: JoinRequest):
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{UPSTREAM_GAME}/join", json=req.model_dump())
        if r.status_code != 200:
            raise HTTPException(r.status_code, r.text)
    return r.json()
