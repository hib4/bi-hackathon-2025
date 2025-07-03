from fastapi import HTTPException
from models import User
from schema.authSchema import loginSchema,registerSchema
from utils.hash import hash,compare
from utils.jwt import createAccessToken

async def register(body: registerSchema):

    is_user_with_email_exist = await User.get_or_none(email=body.email)
    if is_user_with_email_exist:
        raise HTTPException(status_code= 409, detail= "Email already being use")

    user = await User.create(
        name= body.name,
        email= body.email,
        password= hash(body.password),
        auth= "local"
    )
    return {
        "message": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }

async def login(body: loginSchema):
    user = await User.get_or_none(email=body.email)
    
    if not user:
        raise HTTPException(status_code= 404, detail= f"User with email {body.email} not found")

    isMatch = compare(body.password, user.password)

    if not isMatch:
        raise HTTPException(status_code= 401, detail= "Password in correct")

    token = createAccessToken(user)

    return {
        "token": token
    }