import sys
import pathlib
import pytest
import pytest_asyncio
import httpx
from mongomock_motor import AsyncMongoMockClient
import importlib.util
import importlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
COMMON_PATH = ROOT / "packages" / "common_schemas"
QUIZ_SERVICE_PATH = ROOT / "services" / "quiz-service"
BFF_PATH = ROOT / "apps" / "bff-admin"

sys.path.extend([str(COMMON_PATH), str(QUIZ_SERVICE_PATH)])

from app import main as quiz_main  # type: ignore  # noqa: E402
from app import db as quiz_db  # type: ignore  # noqa: E402

spec = importlib.util.spec_from_file_location("bff_main", BFF_PATH / "app" / "main.py")
bff_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bff_main)
quizzes_module = importlib.import_module(f"{bff_main.__name__}.routes.quizzes")


@pytest_asyncio.fixture
async def client(monkeypatch):
    client_db = AsyncMongoMockClient()
    quiz_db.db = client_db["testdb"]
    quiz_main.db = quiz_db.db

    class PatchedAsyncClient(httpx.AsyncClient):
        def __init__(self, *args, **kwargs):
            kwargs.setdefault("app", quiz_main.app)
            kwargs.setdefault("base_url", "http://quiz-service:8000")
            return super().__init__(*args, **kwargs)

    monkeypatch.setattr(quizzes_module.httpx, "AsyncClient", PatchedAsyncClient)
    monkeypatch.setattr(quizzes_module, "UPSTREAM_QUIZ", "http://quiz-service:8000")

    async with httpx.AsyncClient(app=bff_main.app, base_url="http://test") as client:
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
async def test_proxy_crud(client):
    resp = await client.post("/admin/quizzes", json=sample_quiz())
    assert resp.status_code == 200
    quiz_id = resp.json()["id"]

    resp = await client.get(f"/admin/quizzes/{quiz_id}")
    assert resp.status_code == 200

    payload = sample_quiz("Updated Quiz")
    resp = await client.put(f"/admin/quizzes/{quiz_id}", json=payload)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Quiz"

    resp = await client.get("/admin/quizzes", params={"limit": 10, "offset": 0})
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    resp = await client.delete(f"/admin/quizzes/{quiz_id}")
    assert resp.status_code == 200

    resp = await client.get(f"/admin/quizzes/{quiz_id}")
    assert resp.status_code == 404
