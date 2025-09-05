from fastapi import FastAPI, HTTPException
from bson import ObjectId
from common_schemas import Quiz
from .db import db

app = FastAPI(title="quiz-service")

@app.get("/healthz")
async def health():
    return {"status": "ok"}

@app.post("/quizzes", response_model=Quiz)
async def create_quiz(payload: Quiz):
    data = payload.model_dump()
    res = await db.quizzes.insert_one(data)
    data["id"] = str(res.inserted_id)
    return Quiz(**data)

@app.get("/quizzes/{quiz_id}", response_model=Quiz)
async def get_quiz(quiz_id: str):
    try:
        _id = ObjectId(quiz_id)
    except Exception:
        raise HTTPException(400, "invalid id")
    doc = await db.quizzes.find_one({"_id": _id})
    if not doc:
        raise HTTPException(404, "quiz not found")
    doc["id"] = str(doc.pop("_id"))
    return Quiz(**doc)
