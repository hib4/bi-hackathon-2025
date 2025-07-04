from fastapi import APIRouter
from handler import auth_handler
from schema.request import auth_schema

router = APIRouter()

@router.post("/api/v1/auth/register", status_code=201)
async def register(
    body: auth_schema.register_schema
):
    return await auth_handler.register(body)

@router.post("/api/v1/auth/login", status_code=200)
async def login(
    body: auth_schema.login_schema
):
    return await auth_handler.login(body)

@router.post("/api/v1/auth/google", status_code=200)
async def auth_google(
    body: auth_schema.google_login_schema
):
    return await auth_handler.google_login(body)