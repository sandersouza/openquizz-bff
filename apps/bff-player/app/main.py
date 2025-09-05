import os
import httpx
from fastapi import FastAPI, HTTPException
from common_schemas import JoinRequest

UPSTREAM_GAME = os.getenv("UPSTREAM_GAME", "http://game-service:8000")

app = FastAPI(title="bff-player")

@app.get("/player/healthz")
async def health():
    return {"status": "ok"}

@app.post("/player/join")
async def join(req: JoinRequest):
    # MVP: placeholder - valida upstream e retorna instruções
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{UPSTREAM_GAME}/healthz")
        if r.status_code != 200:
            raise HTTPException(r.status_code, "upstream unavailable")
    return {
        "session_id_hint": "use o PIN recebido ao criar a sessão no admin",
        "ws_url": "/ws/{session_id}",
        "nickname": req.nickname,
    }
