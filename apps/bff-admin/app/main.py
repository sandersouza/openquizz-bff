import os
import httpx
import importlib.util
import sys
from pathlib import Path
from fastapi import FastAPI

UPSTREAM_QUIZ = os.getenv("UPSTREAM_QUIZ", "http://quiz-service:8000")
UPSTREAM_GAME = os.getenv("UPSTREAM_GAME", "http://game-service:8000")

app = FastAPI(title="bff-admin", docs_url="/admin/docs", redoc_url="/admin/redocs", openapi_url="/admin/openapi.json")

def include_route_modules() -> None:
    package_dir = Path(__file__).parent / "routes"
    base_package = __package__ or __name__
    for path in package_dir.glob("*.py"):
        if path.name == "__init__.py":
            continue
        module_name = f"{base_package}.routes.{path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        router = getattr(module, "router", None)
        if router is not None:
            app.include_router(router)

include_route_modules()
