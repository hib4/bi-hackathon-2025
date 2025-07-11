from fastapi import HTTPException
from schema.request.auth_schema import login_schema,register_schema,google_login_schema
from models.user import User, AuthProvider
from utils.hash import hash,compare
from datetime import datetime
from utils.jwt import create_access_token
from google.auth.transport import requests
from google.oauth2 import id_token
from setting.settings import settings

async def register(body: register_schema):
    user = await User.find_one(User.email == body.email)
    if user:
        raise HTTPException(status_code= 409, detail= f"email {body.email} already register")

    user = User(
        name = body.name,
        email = body.email,
        password = hash(body.password),
        auth = AuthProvider.local,
        google_id = None
    )
    
    await user.insert()

    return {
        "message": f"successfully create new user with id {str(user.id)}"
    }

async def login(body: login_schema):
    user = await User.find_one(User.email == body.email)
    
    if not user:
        raise HTTPException(status_code= 404, detail= f"User with email {body.email} not found")

    if user.auth == AuthProvider.google:
        raise HTTPException(status_code= 404, detail= f"User with email {body.email} not found")

    isMatch = compare(body.password, user.password)

    if not isMatch:
        raise HTTPException(status_code= 401, detail= "Password in correct")

    token = create_access_token(user)

    return {
        "token": token
    }

async def google_login(body: google_login_schema):
    id_info = id_token.verify_oauth2_token(
        body.id_token,
        requests.Request(),
        settings.GOOGLE_CLIENT_ID
    )

    if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
        raise ValueError('Wrong issuer.')

    google_user_id = id_info['sub']
    email = id_info['email']
    name = id_info.get('name', '')

    user = await User.find_one(User.email == email)

    if user:
        user.name = name
        user.google_id = google_user_id
        user.updated_at = datetime.utcnow()
        await user.save()
    else:
        user = User(
            name=name,
            email=email,
            password="",
            auth=AuthProvider.google,
            google_id=google_user_id,
        )
        await user.insert()

    access_token = create_access_token(user)

    return {
        "token": access_token
    }
