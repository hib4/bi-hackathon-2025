from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime

class Book(Document):
    user_id: str
    title: str
    theme: list
    language: str
    status: str
    age_group: int
    current_scene: int
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None
    maximum_point: int
    story_flow: dict
    characters: list
    scene: list
    user_story: dict
    cover_img_url: Optional[str] = None
    description: str
    estimated_reading_time: int

    class Settings:
        name = "books"
