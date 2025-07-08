from fastapi import APIRouter, Depends
from middleware.auth_middleware import get_current_user
from handler.analytic_handler import get_analytic
router = APIRouter()

@router.get("/api/v1/analytic")
async def get_child_analytic(current_user=Depends(get_current_user)):
    return await get_analytic(current_user)