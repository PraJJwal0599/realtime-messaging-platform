from sqlalchemy import DateTime, func, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class Message(Base):
    __tablename__ = "messages"

    id : Mapped[int] = mapped_column(primary_key = True)

    conversation_id : Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete = "CASCADE"),
        nullable = False,
        index = True,
    )

    sender_id : Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete = "CASCADE"),
        nullable = False,
        index = True,
    )

    content : Mapped[str] = mapped_column(
        Text,
        nullable = False,
    )

    created_at : Mapped[DateTime] = mapped_column(
        DateTime(timezone = True),
        server_default = func.now(),
    )
