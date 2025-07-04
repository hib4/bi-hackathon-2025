from fastapi import APIRouter, Depends
from middleware.auth_middleware import get_current_user
from utils.flux_1_schnell import generate_image
router = APIRouter()

@router.get("/api/v1/test")
async def test(current_user=Depends(get_current_user)):
    result = await generate_image("A monkey climbing a tree, with a colorful snake coiled around a branch, smiling and extending its body to assist. cartoon style, used for kids")
    return { "data": result}