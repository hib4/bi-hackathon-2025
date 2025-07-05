from pydantic import BaseModel

class Book_Card(BaseModel):
    id: str
    title: str
    language: str
    short_description: str
    Estimation_time_to_read: str
    img_cover_url: str
    created_at: str
