from pydantic import BaseModel

class registerSchema(BaseModel):
    name: str
    email: str
    password: str

class loginSchema(BaseModel):
    email: str
    password: str