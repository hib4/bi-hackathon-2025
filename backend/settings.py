from dotenv import load_dotenv
from pydantic_settings import BaseSettings
import os

load_dotenv()

class Settings(BaseSettings):
    HOST: str = os.getenv("HOST")
    PORT: int = int(os.getenv("PORT", "8000"))
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SEALION_API_KEY: str = os.getenv("SEALION_API_KEY")
    JWT_SECRET: str =  os.getenv("JWT_SECRET")
    JWT_EXPIRED: int = int(os.getenv("JWT_EXPIRED", 1))

settings = Settings()