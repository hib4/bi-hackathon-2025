from fastapi import APIRouter, Depends
from middleware.auth_middleware import get_current_user
from schema.request.book_schema import create_book_schema
from handler import book_handler

router = APIRouter()

@router.post("/api/v1/book", status_code=201)
async def register(
    body: create_book_schema,
    current_user = Depends(get_current_user)
):
    return await book_handler.create_book(body, current_user)

@router.get("/api/v1/books", status_code=200)
async def get_books(
    current_user = Depends(get_current_user)
):
    return await book_handler.get_books(current_user)

@router.get("/api/v1/book/{id}", status_code=200)
async def get_book_by_id(
    id: str,
    current_user = Depends(get_current_user)
):
    return await book_handler.get_book_by_id(id,current_user)
