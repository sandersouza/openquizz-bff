from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os, random
from common_schemas import SessionCreate, SessionState
from .broker import publish, redis, PIN_PREFIX

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/openquiz")
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_default_database()

app = FastAPI(title="game-service")

@app.get("/healthz")
async def health():
    pong = await redis.ping()
    return {"status": "ok", "redis": pong}

class SessionOut(SessionState):
    pin: str

@app.get("/sessions/{session_id}", response_model=SessionOut)
async def get_session(session_id: str):
    try:
        _id = ObjectId(session_id)
    except Exception:
        raise HTTPException(400, "invalid id")
    s = await db.sessions.find_one({"_id": _id})
    if not s:
        raise HTTPException(404, "session not found")
    return SessionOut(
        session_id=session_id,
        state=s.get("state", "lobby"),
        current_q_idx=int(s.get("current_q_idx", 0)),
        pin=s.get("pin", ""),
    )

@app.post("/sessions", response_model=SessionOut)
async def create_session(payload: SessionCreate):
    pin = str(random.randint(100000, 999999))
    doc = {
        "quiz_id": payload.quiz_id,
        "state": "lobby",
        "current_q_idx": 0,
        "pin": pin,
    }
    res = await db.sessions.insert_one(doc)
    session_id = str(res.inserted_id)
    await redis.setex(PIN_PREFIX + pin, 3600, session_id)
    await publish(session_id, {"type": "lobby", "session_id": session_id})
    return SessionOut(session_id=session_id, state="lobby", current_q_idx=0, pin=pin)

@app.post("/sessions/{session_id}/start", response_model=SessionState)
async def start_session(session_id: str):
    try:
        _id = ObjectId(session_id)
    except Exception:
        raise HTTPException(400, "invalid id")
    updated = await db.sessions.update_one({"_id": _id}, {"$set": {"state": "question", "current_q_idx": 0}})
    if not updated.modified_count:
        raise HTTPException(404, "session not found")
    await publish(session_id, {"type": "question", "idx": 0})
    return SessionState(session_id=session_id, state="question", current_q_idx=0)

@app.post("/sessions/{session_id}/next", response_model=SessionState)
async def next_question(session_id: str):
    try:
        _id = ObjectId(session_id)
    except Exception:
        raise HTTPException(400, "invalid id")
    s = await db.sessions.find_one({"_id": _id})
    if not s:
        raise HTTPException(404, "session not found")
    nxt = int(s.get("current_q_idx", 0)) + 1
    await db.sessions.update_one({"_id": _id}, {"$set": {"state": "question", "current_q_idx": nxt}})
    await publish(session_id, {"type": "question", "idx": nxt})
    return SessionState(session_id=session_id, state="question", current_q_idx=nxt)

@app.post("/sessions/{session_id}/end", response_model=SessionState)
async def end_session(session_id: str):
    try:
        _id = ObjectId(session_id)
    except Exception:
        raise HTTPException(400, "invalid id")
    updated = await db.sessions.update_one({"_id": _id}, {"$set": {"state": "ended"}})
    if not updated.modified_count:
        raise HTTPException(404, "session not found")
    await publish(session_id, {"type": "ended"})
    return SessionState(session_id=session_id, state="ended", current_q_idx=-1)
