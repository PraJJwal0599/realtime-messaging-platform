from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.auth_dependencies import get_current_user
from app.models.message import Message
from app.models.conversation_participant import ConversationParticipant
from app.models.user import User
from app.schemas.message import MessageCreate

router = APIRouter(prefix = "/messages", tags = ["messages"])

@router.post("", status_code = status.HTTP_201_CREATED)
async def send_message(
    message_in: MessageCreate,
    current_user: User = Depends(get_current_user),
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ConversationParticipant).where(
                ConversationParticipant.conversation_id == message_in.conversation_id,
                ConversationParticipant.user_id == current_user.id,
                ConversationParticipant.left_at.is_(None),
            )
        )

        participant = result.scalar_one_or_none()

        if not participant:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "You are not a participant in this conversation",
            )
        
        message = Message(
            conversation_id = message_in.conversation_id,
            sender_id = current_user.id,
            content = message_in.content,
        )

        session.add(message)
        await session.commit()
        await session.refresh(message)

        return{
            "message_id": message.id,
            "conversation_id": message.conversation_id,
            "sender_id": message.sender_id,
            "content": message.content,
            "created_at": message.created_at
        }
    

@router.get("/{conversation_id}")
async def get_messages(
    conversation_id: int,
    before: int | None = None,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ConversationParticipant).where(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.user_id == current_user.id,
                ConversationParticipant.left_at.is_(None),
            )
        )

        participant = result.scalar_one_or_none()

        if not participant:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "You are not a participant in this Conversation",
            )
        
        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
        )

        if before:
            query = query.where(Message.id < before)

        query = (    
            query.order_by(Message.id.desc())
            .limit(limit)
        )

        result = await session.execute(query)
        messages = result.scalars().all()
        messages.reverse()

        return [
            {
                "message_id": msg.id,
                "sender_id": msg.sender_id,
                "content_at": msg.content,
                "created_at": msg.created_at,
            }
            for msg in messages
        ]