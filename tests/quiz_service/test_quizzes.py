import sys
import pathlib
import sys
import pytest
import pytest_asyncio
import httpx
from mongomock_motor import AsyncMongoMockClient

# Add paths for quiz-service and shared schemas
ROOT = pathlib.Path(__file__).resolve().parents[2]
SERVICE_PATH = ROOT / "services" / "quiz-service"
COMMON_PATH = ROOT / "packages" / "common_schemas"
sys.path.extend([str(SERVICE_PATH), str(COMMON_PATH)])

from app import main as quiz_main
from app import db as quiz_db


@pytest_asyncio.fixture
async def client():
    # use in-memory mongo
    client = AsyncMongoMockClient()
    quiz_db.db = client["testdb"]
    quiz_main.db = quiz_db.db
    async with httpx.AsyncClient(app=quiz_main.app, base_url="http://test") as client:
        yield client


def sample_quiz(title="Sample Quiz"):
    return {
        "title": title,
        "questions": [
            {
                "id": "q1",
                "text": "1+1?",
                "options": ["1", "2"],
                "correct": [1],
                "time_limit_s": 20,
            }
        ],
    }


@pytest.mark.asyncio
async def test_crud_cycle(client):
    # create
    resp = await client.post("/quizzes", json=sample_quiz())
    assert resp.status_code == 200
    data = resp.json()
    quiz_id = data["id"]

    # read
    resp = await client.get(f"/quizzes/{quiz_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == quiz_id

    # update
    payload = sample_quiz("Updated Quiz")
    resp = await client.put(f"/quizzes/{quiz_id}", json=payload)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Quiz"

    # list
    resp = await client.get("/quizzes", params={"limit": 10, "offset": 0})
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # delete
    resp = await client.delete(f"/quizzes/{quiz_id}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "deleted"
