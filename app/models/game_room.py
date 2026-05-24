from datetime import datetime
from typing import List

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class GameRoom(Base):
    __tablename__ = "game_rooms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    host_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    image_set_id: Mapped[int | None] = mapped_column(ForeignKey("image_sets.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="waiting")
    max_players: Mapped[int] = mapped_column(default=4)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    players: Mapped[List["RoomPlayer"]] = relationship(
        back_populates="room", cascade="all, delete-orphan"
    )


class RoomPlayer(Base):
    __tablename__ = "room_players"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("game_rooms.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(20), default="joined")
    joined_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(nullable=True)
    score: Mapped[int] = mapped_column(default=0)
    lives_left: Mapped[int] = mapped_column(default=5)

    room: Mapped["GameRoom"] = relationship(back_populates="players")
    user: Mapped["User"] = relationship(back_populates="rooms")

    @property
    def username(self) -> str | None:
        return self.user.username if self.user else None
