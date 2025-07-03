from fastapi import HTTPException
from models import User
from schema.authSchema import createBookSchema
from utils.ai import get_prompt_schema

