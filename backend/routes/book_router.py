from fastapi import APIRouter, Depends
from middleware.auth_middleware import get_current_user
from schema.book_schema import create_book_schema
from handler import book_handler

router = APIRouter()

@router.post("/api/v1/book", status_code=201)
async def register(
    body: create_book_schema,
    current_user = Depends(get_current_user)
):
    return await book_handler.create_book(body, current_user)
