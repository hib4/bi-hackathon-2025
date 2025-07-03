from pydantic import BaseModel
from enum import Enum

class LanguageEnum(str, Enum):
    ENGLISH = "english"
    CHINESE = "chinese"
    MALAY = "malay"
    TAGALOG = "tagalog"
    TAMIL = "tamil"
    KHMER = "khmer"
    VIETNAM = "vietnam"
    THAI = "thai"
    INDONESIAN = "indonesian"

class createBookSchema(BaseModel):
    prompt: str
    language: LanguageEnum