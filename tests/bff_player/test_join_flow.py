import pathlib
import sys
import types
from types import SimpleNamespace
import importlib
import importlib.util

import httpx
import pytest
import pytest_asyncio
from mongomock_motor import AsyncMongoMockClient

ROOT = pathlib.Path(__file__).resolve().parents[2]
COMMON_PATH = ROOT / "packages" / "common_schemas"
GAME_SERVICE_PATH = ROOT / "services" / "game-service" / "app"
BFF_PLAYER_PATH = ROOT / "apps" / "bff-player" / "app"

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


game_main = load_service(GAME_SERVICE_PATH, "game_service_join_app")
bff_player_main = load_service(BFF_PLAYER_PATH, "bff_player_app")
join_module = importlib.import_module("bff_player_app.routes.join")


@pytest_asyncio.fixture
async def client(monkeypatch):
    gclient = AsyncMongoMockClient()
    game_main.db = gclient["testdb"]

    class FakeRedis:
        def __init__(self):
            self.store = {}

        async def setex(self, key, ttl, value):
            self.store[key] = {"ttl": ttl, "value": value}

        async def get(self, key):
            data = self.store.get(key)
            return data["value"] if data else None

        async def ping(self):
            return True

    fake_redis = FakeRedis()
    monkeypatch.setattr(game_main, "redis", fake_redis)

    async def fake_publish(room, event):
        return None

    monkeypatch.setattr(game_main, "publish", fake_publish)

    class PatchedGameClient(httpx.AsyncClient):
        def __init__(self, *args, **kwargs):
            kwargs.setdefault("app", game_main.app)
            kwargs.setdefault("base_url", "http://game-service:8000")
            super().__init__(*args, **kwargs)

    monkeypatch.setattr(join_module, "httpx", SimpleNamespace(AsyncClient=PatchedGameClient))
    monkeypatch.setattr(join_module, "UPSTREAM_GAME", "http://game-service:8000")

    async with httpx.AsyncClient(app=bff_player_main.app, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_join_with_valid_pin_returns_session(client):
    create_resp = await client.post("/player/join", json={"pin": "999999", "nickname": "Ana"})
    assert create_resp.status_code == 404

    async with httpx.AsyncClient(app=game_main.app, base_url="http://game-service:8000") as game_client:
        session_resp = await game_client.post("/sessions", json={"quiz_id": "quiz-1"})
    assert session_resp.status_code == 200
    data = session_resp.json()

    join_resp = await client.post("/player/join", json={"pin": data["pin"], "nickname": "Ana"})
    assert join_resp.status_code == 200
    body = join_resp.json()
    assert body["session_id"] == data["session_id"]
    assert body["nickname"] == "Ana"
    assert body["ws_url"] == f"/ws/{data['session_id']}"
