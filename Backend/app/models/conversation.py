from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id : Mapped[int] = mapped_column(primary_key = True)

    is_group : Mapped[bool] = mapped_column(
        Boolean,
        default = False,
        nullable = False,
    )

    created_at : Mapped[DateTime] = mapped_column(
        DateTime(timezone = True),
        server_default = func.now(),
    ) 

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )