from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.auth_dependencies import get_current_user
from app.models.user import User
from app.models.conversation import Conversation
from app.models.conversation_participant import ConversationParticipant
from app.models.message import Message

router = APIRouter(prefix = "/conversations", tags = ["conversations"])

@router.post("/direct/{username}")
async def create_or_get_direct_conversation(
    username: str,
    current_user: User = Depends(get_current_user),
):
    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(User).where(User.username == username)
        )
        target_user = result.scalar_one_or_none()

        if not target_user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User not found",
            )
        
        if target_user.id == current_user.id:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Cannot start a converstion with yourself",
            )
        
        stmt = (
            select(Conversation).
            join(ConversationParticipant)
            .where(
                Conversation.is_group == False,
                ConversationParticipant.user_id.in_(
                    [current_user.id, target_user.id]
                ),
            )
            .group_by(Conversation.id)
            .having(
                func.count(ConversationParticipant.user_id) == 2
            )
        )

        result = await session.execute(stmt)
        conversation = result.scalar_one_or_none()

        if conversation:
            return {"conversation_id": conversation.id}
        
        conversation = Conversation(is_group = False)
        session.add(conversation)
        await session.flush()

        session.add_all ([
            ConversationParticipant(
                conversation_id = conversation.id,
                user_id = current_user.id,
                role = "member"
            ),
            ConversationParticipant(
                conversation_id = conversation.id,
                user_id = target_user.id,
                role = "member"
            ),
        ])

        await session.commit()
        
        return {"conversation_id": conversation.id}
    
@router.get("")
async def list_conversations(
    current_user: User = Depends(get_current_user),
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Conversation)
            .join(ConversationParticipant)
            .where(
                ConversationParticipant.user_id == current_user.id,
                ConversationParticipant.left_at.is_(None),
            )
            .order_by(Conversation.updated_at.desc())
        )

        conversations = result.scalars().all()

        response = []

        for convo in conversations:
            participant_result = await session.execute(
                select(ConversationParticipant).where(
                    ConversationParticipant.conversation_id == convo.id,
                    ConversationParticipant.user_id == current_user.id,
                )
            )

            participant = participant_result.scalar_one_or_none()
            if not participant:
                continue

            unread_query = select(func.count(Message.id)).where(
                Message.conversation_id == convo.id,
                Message.sender_id != current_user.id,
            )

            if participant.last_read_message_id:
                unread_query = unread_query.where(
                    Message.id > participant.last_read_message_id
            )
        
            unread_result = await session.execute(unread_query)
            unread_count = unread_result.scalar_one()

        
            participants_result = await session.execute(
                select(User)
                .join(ConversationParticipant)
                .where(
                    ConversationParticipant.conversation_id == convo.id,
                    ConversationParticipant.user_id != current_user.id,
                )
            )
                
            other_user = participants_result.scalar_one_or_none()         

            last_message_result = await session.execute(
                select(Message)
                .where(Message.conversation_id == convo.id)
                .order_by(Message.id.desc())
                .limit(1)
            )       

            last_message = last_message_result.scalar_one_or_none()

            response.append({
                "conversation_id" : convo.id,
                "is_group" : convo.is_group,
                "other_user" : {
                    "id" : other_user.id,
                    "username" : other_user.username,
                    "display_name" : other_user.display_name,
                } if other_user else None,
                "last_message" : {
                    "content" : last_message.content,
                    "created_at" : last_message.created_at,
                } if last_message else None,
                "unread_count": unread_count,
            })

        return response
        
@router.post("/{conversation_id}/read")
async def mark_conversation_as_read(
    conversation_id : int,
    current_user : User = Depends(get_current_user),
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
                detail = "You are not a participant of the conversation",
            )
        
        result = await session.execute(
            select(Message.id)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.id.desc())
            .limit(1)
        )

        latest_message_id = result.scalar_one_or_none()

        if latest_message_id:
            participant.last_read_message_id = latest_message_id
            await session.commit()

        return {"status": "conversation marked as read"}
