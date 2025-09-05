import os
import httpx
from fastapi import APIRouter, HTTPException
from common_schemas import SessionCreate

UPSTREAM_GAME = os.getenv("UPSTREAM_GAME", "http://game-service:8000")

router = APIRouter()


@router.post("/admin/sessions", summary="Create session")
async def create_session(payload: SessionCreate):
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{UPSTREAM_GAME}/sessions", json=payload.model_dump())
        if r.status_code != 200:
            raise HTTPException(r.status_code, r.text)
        return r.json()


@router.post("/admin/sessions/{session_id}/start", summary="Start session")
async def start_session(session_id: str):
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{UPSTREAM_GAME}/sessions/{session_id}/start")
        if r.status_code != 200:
            raise HTTPException(r.status_code, r.text)
        return r.json()
