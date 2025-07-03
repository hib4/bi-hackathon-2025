from fastapi import APIRouter
from handler import auth_handler
from schema.auth_schema import register_schema,login_schema

router = APIRouter()

@router.post("/api/v1/auth/register", status_code=201)
async def register(
    body: register_schema
):
    return await auth_handler.register(body)

@router.post("/api/v1/auth/login", status_code=200)
async def login(
    body: login_schema
):
    return await auth_handler.login(body)