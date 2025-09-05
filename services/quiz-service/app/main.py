from fastapi import FastAPI, HTTPException
from fastapi import Query
from bson import ObjectId
from common_schemas import Quiz
from .db import db

app = FastAPI(title="quiz-service")


@app.on_event("startup")
async def create_indexes():
    await db.quizzes.create_index("title")


@app.get("/healthz", summary="Health check")
async def health():
    return {"status": "ok"}


@app.post("/quizzes", response_model=Quiz, summary="Create quiz")
async def create_quiz(payload: Quiz):
    data = payload.model_dump()
    res = await db.quizzes.insert_one(data)
    data["id"] = str(res.inserted_id)
    return Quiz(**data)


@app.get("/quizzes/{quiz_id}", response_model=Quiz, summary="Get quiz")
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


@app.get("/quizzes", response_model=list[Quiz], summary="List quizzes")
async def list_quizzes(limit: int = Query(10, ge=1), offset: int = Query(0, ge=0)):
    cursor = db.quizzes.find().skip(offset).limit(limit)
    quizzes = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        quizzes.append(Quiz(**doc))
    return quizzes


@app.put("/quizzes/{quiz_id}", response_model=Quiz, summary="Update quiz")
async def update_quiz(quiz_id: str, payload: Quiz):
    try:
        _id = ObjectId(quiz_id)
    except Exception:
        raise HTTPException(400, "invalid id")
    data = payload.model_dump(exclude={"id"})
    updated = await db.quizzes.update_one({"_id": _id}, {"$set": data})
    if not updated.matched_count:
        raise HTTPException(404, "quiz not found")
    doc = await db.quizzes.find_one({"_id": _id})
    doc["id"] = str(doc.pop("_id"))
    return Quiz(**doc)


@app.delete("/quizzes/{quiz_id}", summary="Delete quiz")
async def delete_quiz(quiz_id: str):
    try:
        _id = ObjectId(quiz_id)
    except Exception:
        raise HTTPException(400, "invalid id")
    res = await db.quizzes.delete_one({"_id": _id})
    if not res.deleted_count:
        raise HTTPException(404, "quiz not found")
    return {"status": "deleted"}
