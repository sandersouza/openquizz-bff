import sys
import pathlib
import types
import pytest
import pytest_asyncio
import httpx
from mongomock_motor import AsyncMongoMockClient
import importlib.util
import importlib
from types import SimpleNamespace

ROOT = pathlib.Path(__file__).resolve().parents[2]
COMMON_PATH = ROOT / "packages" / "common_schemas"
QUIZ_SERVICE_PATH = ROOT / "services" / "quiz-service" / "app"
GAME_SERVICE_PATH = ROOT / "services" / "game-service" / "app"
BFF_PATH = ROOT / "apps" / "bff-admin" / "app"

sys.path.extend([str(COMMON_PATH)])


def load_service(path: pathlib.Path, pkg_name: str):
    pkg = types.ModuleType(pkg_name)
    pkg.__path__ = [str(path)]
    sys.modules[pkg_name] = pkg
    spec = importlib.util.spec_from_file_location(f"{pkg_name}.main", path / "main.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{pkg_name}.main"] = module
    spec.loader.exec_module(module)
    return module

quiz_main = load_service(QUIZ_SERVICE_PATH, "quiz_service_app")
quiz_db = quiz_main.db

game_main = load_service(GAME_SERVICE_PATH, "game_service_app")

bff_main = load_service(BFF_PATH, "bff_admin_app")
quizzes_module = importlib.import_module("bff_admin_app.routes.quizzes")
sessions_module = importlib.import_module("bff_admin_app.routes.sessions")


@pytest_asyncio.fixture
async def client(monkeypatch):
    qclient = AsyncMongoMockClient()
    quiz_db.db = qclient["testdb"]
    quiz_main.db = quiz_db.db

    gclient = AsyncMongoMockClient()
    game_main.db = gclient["testdb"]

    class FakeRedis:
        def __init__(self):
            self.store = {}
        async def setex(self, key, ttl, value):
            self.store[key] = {"ttl": ttl, "value": value}
        async def ping(self):
            return True
    fake_redis = FakeRedis()
    published = []
    async def fake_publish(room, event):
        published.append((room, event))
    monkeypatch.setattr(game_main, "redis", fake_redis)
    monkeypatch.setattr(game_main, "publish", fake_publish)

    class PatchedQuizClient(httpx.AsyncClient):
        def __init__(self, *args, **kwargs):
            kwargs.setdefault("app", quiz_main.app)
            kwargs.setdefault("base_url", "http://quiz-service:8000")
            super().__init__(*args, **kwargs)

    class PatchedGameClient(httpx.AsyncClient):
        def __init__(self, *args, **kwargs):
            kwargs.setdefault("app", game_main.app)
            kwargs.setdefault("base_url", "http://game-service:8000")
            super().__init__(*args, **kwargs)

    monkeypatch.setattr(quizzes_module, "httpx", SimpleNamespace(AsyncClient=PatchedQuizClient))
    monkeypatch.setattr(quizzes_module, "UPSTREAM_QUIZ", "http://quiz-service:8000")
    monkeypatch.setattr(sessions_module, "httpx", SimpleNamespace(AsyncClient=PatchedGameClient))
    monkeypatch.setattr(sessions_module, "UPSTREAM_GAME", "http://game-service:8000")

    async with httpx.AsyncClient(app=bff_main.app, base_url="http://test") as client:
        client.fake_redis = fake_redis
        client.published = published
        client.pin_prefix = game_main.PIN_PREFIX
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
async def test_session_flow(client):
    resp = await client.post("/admin/quizzes", json=sample_quiz())
    assert resp.status_code == 200
    quiz_id = resp.json()["id"]

    resp = await client.post("/admin/sessions", json={"quiz_id": quiz_id})
    assert resp.status_code == 200
    data = resp.json()
    session_id = data["session_id"]
    pin = data["pin"]
    key = client.pin_prefix + pin
    assert client.fake_redis.store[key]["ttl"] == 3600

    resp = await client.post(f"/admin/sessions/{session_id}/start")
    assert resp.status_code == 200
    assert resp.json()["state"] == "question"

    resp = await client.post(f"/admin/sessions/{session_id}/next")
    assert resp.status_code == 200
    assert resp.json()["current_q_idx"] == 1

    resp = await client.post(f"/admin/sessions/{session_id}/end")
    assert resp.status_code == 200
    assert resp.json()["state"] == "ended"

    resp = await client.get(f"/admin/sessions/{session_id}")
    assert resp.status_code == 200
    assert resp.json()["state"] == "ended"

    assert client.published == [
        (session_id, {"type": "lobby", "session_id": session_id}),
        (session_id, {"type": "question", "idx": 0}),
        (session_id, {"type": "question", "idx": 1}),
        (session_id, {"type": "ended"}),
    ]
