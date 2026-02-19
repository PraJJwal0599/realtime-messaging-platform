from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from app.core.config import APP_NAME
from app.core.init_db import init_db
from app.routes import auth
from fastapi.security import HTTPBearer
from app.core.config import APP_NAME
from app.routes.conversations import router as conversations_router
from app.routes.messages import router as messages_router
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.message import Message
from datetime import datetime
from jose import jwt, JWTError
from app.core.config import JWT_SECRET, JWT_ALGORITHM
from app.models.user import User
from sqlalchemy import select
import os
from app.routes.notifications import router as notifications_router
from app.models.conversation_participant import ConversationParticipant
from app.routes.notifications import manager as notification_manager
from app.models.conversation import Conversation
from sqlalchemy import update

app = FastAPI(title = APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
         "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, conversation_id: int):
        await websocket.accept()
        # 2 lines below
        print("Connect called with conversation_id:", conversation_id)

        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = []

        self.active_connections[conversation_id].append(websocket)

        print("Active connections:", self.active_connections)

    def disconnect(self, websocket: WebSocket, conversation_id: int):
        self.active_connections[conversation_id].remove(websocket)

        if not self.active_connections[conversation_id]:
            del self.active_connections[conversation_id]
    
    async def broadcast(self, conversation_id: int, message: dict):
        if conversation_id in self.active_connections:
            for connection in self.active_connections[conversation_id]:
                await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/chat/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: int):

    token = websocket.query_params.get("token")

    if not token:
        await websocket.close()
        return

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            await websocket.close()
            return

    except JWTError:
        await websocket.close()
        return

    # Load user from DB
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.id == int(user_id))
        )
        user = result.scalar_one_or_none()

        if not user:
            await websocket.close()
            return

    # Now user is authenticated
    await manager.connect(websocket, conversation_id)

    try:
        while True:
            data = await websocket.receive_json()
            print("Recieved WS data", data)

            message_type = data.get("type")

            if message_type == "typing":
                print("Broadcasting typing")
                await manager.broadcast(conversation_id, {
                    "type": "typing",
                    "sender_id": user.id
                })
                continue

            content = data.get("content")

            async with AsyncSessionLocal() as session:
                message = Message(
                    conversation_id=conversation_id,
                    sender_id=user.id,
                    content=content,
                )

                session.add(message)
                print("Updating conversation:", conversation_id)

                await session.execute(
                    update(Conversation)
                    .where(Conversation.id == conversation_id)
                    .values(updated_at=datetime.utcnow())
                )
                print("Update committed")

                
                await session.commit()
                await session.refresh(message)

                await manager.broadcast(
                    conversation_id,
                    {
                        "type": "message",
                        "message_id": message.id,
                        "conversation_id": conversation_id,
                        "sender_id": message.sender_id,
                        "content": message.content,
                        "created_at": str(message.created_at),
                    }
                )


                # Find receiver(s)
                result = await session.execute(
                    select(ConversationParticipant.user_id)
                    .where(
                        ConversationParticipant.conversation_id == conversation_id,
                        ConversationParticipant.user_id != user.id
                    )
                )

                receivers = result.scalars().all()

                print("Sending notification to:", receivers)

                for receiver_id in receivers:
                    await notification_manager.send_notification(
                    receiver_id,
                    {
                        "type": "new_message",
                        "conversation_id": conversation_id,
                        "sender_name": user.display_name
                    }
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket, conversation_id)

@app.on_event("startup")
async def on_startup():
    if os.getenv("ENV") != "test":
        await init_db()

@app.get("/")
def health_check():
    return {
        "status" : "ok",
        "app" : "APP_NAME"
    }

app.include_router(messages_router)

app.include_router(conversations_router)

app.include_router(auth.router)

app.include_router(notifications_router)