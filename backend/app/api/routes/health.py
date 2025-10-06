from fastapi import APIRouter

router = APIRouter()

@router.get("/", tags=["Health"])
async def health():
    return {"status": "ok"}
