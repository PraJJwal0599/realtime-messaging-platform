from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy import select

from app.core.config import JWT_SECRET, JWT_ALGORITHM
from app.core.database import AsyncSessionLocal
from app.models.user import User

from fastapi import WebSocket, Query
from jose import JWTError
from app.core.auth_utils import decode_access_token
from app.models.user import User


security = HTTPBearer()

async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms = [JWT_ALGORITHM]
        )

        user_id: str | None = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Invaild token"
            )
    
    except JWTError:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invaild or expired token"
        )
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.id == int(user_id))
        )

        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "User not found"
            )
    
    return user

async def get_current_user_ws(websocket: WebSocket):
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008)
        return

    try:
        payload = decode_access_token(token)
        user_id: int = payload.get("user_id")
    except JWTError:
        await websocket.close(code=1008)
        return

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

    if not user:
        await websocket.close(code=1008)
        return

    return user