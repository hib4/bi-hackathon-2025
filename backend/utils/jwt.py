from jose import jwt, JWTError
from datetime import datetime, timedelta
from setting.settings import settings
from models import User

JWT_SECRET = settings.JWT_SECRET
ALGORITHM = "HS256"
JWT_EXPIRED = 60 * settings.JWT_EXPIRED

def create_access_token(user: User):
    data = {
        "id": str(user.id),
        "name": user.name,
        "email": user.email,
        "auth": user.auth,
        "google_id": user.google_id
    }

    to_encode = data.copy()
    expires_delta: int = JWT_EXPIRED
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None