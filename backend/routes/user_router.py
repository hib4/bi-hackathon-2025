from fastapi import APIRouter, Depends
from middleware.auth_middleware import get_current_user
from handler.user_handler import get_user_profile
router = APIRouter()

@router.get("/api/v1/user")
async def get_profile(current_user=Depends(get_current_user)):
    return await get_user_profile(current_user)