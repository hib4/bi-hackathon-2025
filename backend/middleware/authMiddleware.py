from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.jwt import verifyToken

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verifyToken(token)

    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return payload
