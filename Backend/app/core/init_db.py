from app.core.database import engine
from app.models.base import Base
from app.models.user import User
from app.models.conversation import Conversation
from app.models.conversation_participant import ConversationParticipant
from app.models.message import Message

async def init_db():
    if engine is None:
        return
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)