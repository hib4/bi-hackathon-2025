from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    HOST: str
    PORT: int
    BOOK_STORY_GENERATION_URL: str
    MONGODB_URL: str
    MONGODB_DB: str
    SEALION_API_KEY: str
    FLUX_1_SCHNELL_API_KEY: str
    JWT_SECRET: str
    JWT_EXPIRED: int = 1
    GOOGLE_CLIENT_ID: str
    MICROSOFT_AZURE_BLOB_SAS_TOKEN: str
    MICROSOFT_AZURE_TEXT_TO_SPEECH_RESOURCE_KEY: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
