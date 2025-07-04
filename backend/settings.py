from dotenv import load_dotenv
from pydantic_settings import BaseSettings
import os

load_dotenv()

class Settings(BaseSettings):
    HOST: str = os.getenv("HOST")
    PORT: int = int(os.getenv("PORT", "8000"))
    MONGODB_URL: str = os.getenv("MONGODB_URL")
    MONGODB_DB: str = os.getenv("MONGODB_DB")
    SEALION_API_KEY: str = os.getenv("SEALION_API_KEY")
    FLUX_1_SCHNELL_API_KEY: str = os.getenv("FLUX_1_SCHNELL_API_KEY")
    JWT_SECRET: str =  os.getenv("JWT_SECRET")
    JWT_EXPIRED: int = int(os.getenv("JWT_EXPIRED", 1))
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")

settings = Settings()