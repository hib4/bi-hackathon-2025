from pydantic import BaseModel
from enum import Enum

class language_enum(str, Enum):
    ENGLISH = "english"
    CHINESE = "chinese"
    MALAY = "malay"
    TAGALOG = "tagalog"
    TAMIL = "tamil"
    KHMER = "khmer"
    VIETNAM = "vietnam"
    THAI = "thai"
    INDONESIAN = "indonesian"

class create_book_schema(BaseModel):
    prompt: str
    language: language_enum

class get_book_by_id_schema(BaseModel):
    id: str