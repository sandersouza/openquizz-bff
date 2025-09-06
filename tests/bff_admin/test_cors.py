import pathlib
import importlib.util
import sys

import httpx
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
COMMON_PATH = ROOT / "packages" / "common_schemas"
QUIZ_SERVICE_PATH = ROOT / "services" / "quiz-service"
BFF_PATH = ROOT / "apps" / "bff-admin"

sys.path.extend([str(COMMON_PATH), str(QUIZ_SERVICE_PATH)])

spec = importlib.util.spec_from_file_location("bff_main", BFF_PATH / "app" / "main.py")
bff_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bff_main)


@pytest.mark.asyncio
async def test_cors_allows_admin_localhost():
    origin = "http://admin.localhost"
    async with httpx.AsyncClient(app=bff_main.app, base_url="http://test") as client:
        resp = await client.options(
            "/admin/quizzes",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
            },
        )
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == origin
