from fastapi import APIRouter, Depends
from middleware.authMiddleware import get_current_user

router = APIRouter()

@router.get("/api/v1/test")
async def test(current_user=Depends(get_current_user)):
    return { "message": f"welcome {current_user}"}