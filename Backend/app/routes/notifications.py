from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.core.connection_manager import NotificationManager
from app.core.auth_dependencies import get_current_user_ws
from app.core.auth_utils import decode_access_token
from jose import jwt, JWTError
from app.core.config import (
    JWT_SECRET,
    JWT_ALGORITHM,
    JWT_EXPIRE_MINUTES,
)

router = APIRouter()
manager = NotificationManager()

@router.websocket("/ws/notifications")
async def notification_ws(websocket: WebSocket):


    token = websocket.query_params.get("token")

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )
    except:
        await websocket.close()
        return

    user_id = int(payload.get("sub"))

    await manager.connect(user_id, websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)