from tortoise.contrib.fastapi import register_tortoise
from fastapi import FastAPI
from settings import settings
from routes import routers
import uvicorn

app = FastAPI()

for router in routers:
    app.include_router(router)

register_tortoise(
    app,
    db_url= settings.DATABASE_URL,
    modules={"models": [
        "models.user",
        "models.book",
        "models.page",
        "models.quiz",
        "models.answer"
    ]},
    generate_schemas=True,
    add_exception_handlers=True,
)

if __name__ == "__main__":
    for setting in settings:
        print(setting)

    uvicorn.run(
        "main:app", 
        host= settings.HOST, 
        port= settings.PORT, 
        reload=True
    )