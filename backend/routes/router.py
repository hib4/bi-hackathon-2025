from fastapi import APIRouter
from handler import sealion_handler

router = APIRouter()

@router.get("/gpt/ask")
async def ask_gpt():
    return await sealion_handler.getSealionRespond()