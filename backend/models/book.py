from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime

class Book(Document):
    user_id: str
    title: str
    theme: list
    age_group: str
    language: str
    status: str
    current_scene: int
    started_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None
    maximum_point: int
    story_flow: dict
    characters: list
    scene: list
    user_story: dict

    class Settings:
        name = "books"
