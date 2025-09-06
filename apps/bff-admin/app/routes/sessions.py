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


@router.post("/admin/sessions/{session_id}/next", summary="Next question")
async def next_question(session_id: str):
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{UPSTREAM_GAME}/sessions/{session_id}/next")
        if r.status_code != 200:
            raise HTTPException(r.status_code, r.text)
        return r.json()


@router.post("/admin/sessions/{session_id}/end", summary="End session")
async def end_session(session_id: str):
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{UPSTREAM_GAME}/sessions/{session_id}/end")
        if r.status_code != 200:
            raise HTTPException(r.status_code, r.text)
        return r.json()


@router.get("/admin/sessions/{session_id}", summary="Get session")
async def get_session(session_id: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{UPSTREAM_GAME}/sessions/{session_id}")
        if r.status_code != 200:
            raise HTTPException(r.status_code, r.text)
        return r.json()
