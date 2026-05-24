from datetime import datetime
from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    avatar_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    image_sets: Mapped[List["ImageSet"]] = relationship(back_populates="creator")
    game_sessions: Mapped[List["GameSession"]] = relationship(back_populates="user")
    rooms: Mapped[List["RoomPlayer"]] = relationship(back_populates="user")
