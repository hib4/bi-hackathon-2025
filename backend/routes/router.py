from fastapi import APIRouter
from handler import sealionHandler

router = APIRouter()

@router.get("/gpt/ask")
async def ask_gpt():
    return await sealionHandler.getSealionRespond()