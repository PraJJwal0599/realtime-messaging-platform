from sqlalchemy import String, Boolean, DateTime, func, ForeignKey, Integer, Column
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class ConversationParticipant(Base):
    __tablename__ = "conversation_participants"

    id : Mapped[int] = mapped_column(primary_key = True)

    conversation_id : Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete = "CASCADE"),
        nullable = False,
        index = True,
    )

    user_id : Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete = "CASCADE"),
        nullable = False,
        index = True,
    )

    role : Mapped[str] = mapped_column(
        String(20),
        default = "member",
        nullable = False,
    )

    joined_at : Mapped[DateTime] = mapped_column(
        DateTime(timezone = True),
        server_default = func.now(),
    )

    left_at : Mapped[DateTime] = mapped_column(
        DateTime(timezone = True),
        nullable = True,
    )
    last_read_message_id = Column(Integer, nullable = True)