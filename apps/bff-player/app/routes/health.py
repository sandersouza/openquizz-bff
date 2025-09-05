from fastapi import APIRouter

router = APIRouter()

@router.get("/player/healthz")
async def health():
    return {"status": "ok"}
