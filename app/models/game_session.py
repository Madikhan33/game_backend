from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class GameSession(Base):
    __tablename__ = "game_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    image_set_id: Mapped[int] = mapped_column(ForeignKey("image_sets.id"))
    room_id: Mapped[int | None] = mapped_column(ForeignKey("game_rooms.id"), nullable=True)
    started_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(nullable=True)
    total_score: Mapped[int] = mapped_column(default=0)
    max_combo: Mapped[int] = mapped_column(default=0)
    accuracy_percent: Mapped[float] = mapped_column(Float, default=0.0)
    lives_left: Mapped[int] = mapped_column(default=5)

    user: Mapped["User"] = relationship(back_populates="game_sessions")
    image_set: Mapped["ImageSet"] = relationship(back_populates="game_sessions")
    attempts: Mapped[List["GameAttempt"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
