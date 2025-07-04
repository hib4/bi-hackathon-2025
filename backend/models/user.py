from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from enum import Enum

class AuthProvider(str, Enum):
    local = "local"
    google = "google"

class User(Document):
    name: str
    email: str
    password: str
    auth: AuthProvider
    google_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
