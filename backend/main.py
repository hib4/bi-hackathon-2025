from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError, HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from exceptions import handler as exception_handler
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from setting.settings import settings
from routes import routers
from models.user import User
from models.book import Book
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_beanie(
        database=client[settings.MONGODB_DB],
        document_models=[User,Book],
    )
    yield

app = FastAPI(lifespan=lifespan)

for router in routers:
    app.include_router(router)

app.add_exception_handler(RequestValidationError, exception_handler.validation_exception_handler)
app.add_exception_handler(HTTPException, exception_handler.http_exception_handler)
app.add_exception_handler(StarletteHTTPException, exception_handler.starlette_http_exception_handler)
app.add_exception_handler(Exception, exception_handler.internal_server_error_handler)

if __name__ == "__main__":
    for setting in settings:
        print(setting)

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT
    )