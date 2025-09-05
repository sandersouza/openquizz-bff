from fastapi import APIRouter

router = APIRouter()


@router.get("/healthz", summary="Health check")
async def root_health():
    return {"status": "ok"}


@router.get("/admin/healthz", summary="Admin health")
async def health():
    return {"status": "ok"}
