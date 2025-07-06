from pydantic import BaseModel

class Book_Card(BaseModel):
    id: str
    title: str
    language: str
    description: str
    estimation_time_to_read: str
    cover_img_url: str | None
    created_at: str
