from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key = True)

    email : Mapped[str] = mapped_column(
        String(255),
        unique = True,
        index = True,
        nullable = False,
    )

    username : Mapped[str] = mapped_column(
        String(50),
        unique = True,
        index = True,
        nullable = False,
    )

    display_name: Mapped[str] = mapped_column(
        String(100),
        nullable = False,
    )

    password_hash : Mapped[str] = mapped_column(nullable = False)

    is_active : Mapped[bool] = mapped_column(
        Boolean,
        default = True,
        nullable = False,
    )

    created_at : Mapped[DateTime] = mapped_column(
        DateTime(timezone = True),
        server_default = func.now()
    )

