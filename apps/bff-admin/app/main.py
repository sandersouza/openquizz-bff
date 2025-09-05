import os
import httpx
from fastapi import FastAPI, HTTPException
from common_schemas import Quiz, SessionCreate

UPSTREAM_QUIZ = os.getenv("UPSTREAM_QUIZ", "http://quiz-service:8000")
UPSTREAM_GAME = os.getenv("UPSTREAM_GAME", "http://game-service:8000")

app = FastAPI(title="bff-admin")

@app.get("/admin/healthz")
async def health():
    return {"status": "ok"}

@app.post("/admin/quizzes", response_model=Quiz)
async def create_quiz(payload: Quiz):
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{UPSTREAM_QUIZ}/quizzes", json=payload.model_dump())
        if r.status_code != 200:
            raise HTTPException(r.status_code, r.text)
        return Quiz(**r.json())

@app.post("/admin/sessions")
async def create_session(payload: SessionCreate):
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{UPSTREAM_GAME}/sessions", json=payload.model_dump())
        if r.status_code != 200:
            raise HTTPException(r.status_code, r.text)
        return r.json()

@app.post("/admin/sessions/{session_id}/start")
async def start_session(session_id: str):
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{UPSTREAM_GAME}/sessions/{session_id}/start")
        if r.status_code != 200:
            raise HTTPException(r.status_code, r.text)
        return r.json()
