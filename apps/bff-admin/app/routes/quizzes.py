import os
import httpx
from fastapi import APIRouter, HTTPException, Response
from common_schemas import Quiz

UPSTREAM_QUIZ = os.getenv("UPSTREAM_QUIZ", "http://quiz-service:8000")

router = APIRouter()


@router.post("/admin/quizzes", response_model=Quiz, summary="Create quiz")
async def create_quiz(payload: Quiz):
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{UPSTREAM_QUIZ}/quizzes", json=payload.model_dump())
        if r.status_code != 200:
            raise HTTPException(r.status_code, r.text)
        return Quiz(**r.json())


@router.get("/admin/quizzes/{quiz_id}", response_model=Quiz, summary="Get quiz")
async def get_quiz(quiz_id: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{UPSTREAM_QUIZ}/quizzes/{quiz_id}")
        if r.status_code != 200:
            raise HTTPException(r.status_code, r.text)
        return Quiz(**r.json())


@router.get("/admin/quizzes", response_model=list[Quiz], summary="List quizzes")
async def list_quizzes(limit: int = 10, offset: int = 0):
    params = {"limit": limit, "offset": offset}
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{UPSTREAM_QUIZ}/quizzes", params=params)
        if r.status_code != 200:
            raise HTTPException(r.status_code, r.text)
        return [Quiz(**item) for item in r.json()]


@router.put("/admin/quizzes/{quiz_id}", response_model=Quiz, summary="Update quiz")
async def update_quiz(quiz_id: str, payload: Quiz):
    async with httpx.AsyncClient() as client:
        r = await client.put(f"{UPSTREAM_QUIZ}/quizzes/{quiz_id}", json=payload.model_dump())
        if r.status_code != 200:
            raise HTTPException(r.status_code, r.text)
        return Quiz(**r.json())


@router.delete("/admin/quizzes/{quiz_id}", summary="Delete quiz")
async def delete_quiz(quiz_id: str):
    async with httpx.AsyncClient() as client:
        r = await client.delete(f"{UPSTREAM_QUIZ}/quizzes/{quiz_id}")
        if r.status_code != 200:
            raise HTTPException(r.status_code, r.text)
        if r.content:
            return r.json()
        return Response(status_code=r.status_code)
