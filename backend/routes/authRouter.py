from fastapi import APIRouter
from handler import authHandler
from schema.authSchema import registerSchema,loginSchema

router = APIRouter()

@router.post("/api/v1/auth/register", status_code=201)
async def register(
    body: registerSchema
):
    return await authHandler.register(body)

@router.post("/api/v1/auth/login", status_code=200)
async def login(
    body: loginSchema
):
    return await authHandler.login(body)