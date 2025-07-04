from pydantic import BaseModel

class register_schema(BaseModel):
    name: str
    email: str
    password: str

class login_schema(BaseModel):
    email: str
    password: str

class google_login_schema(BaseModel):
    id_token: str