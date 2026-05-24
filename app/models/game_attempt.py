from datetime import datetime

from sqlalchemy import ForeignKey, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class GameAttempt(Base):
    __tablename__ = "game_attempts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("game_sessions.id"))
    x: Mapped[float] = mapped_column(Float)
    y: Mapped[float] = mapped_column(Float)
    is_hit: Mapped[bool] = mapped_column(Boolean, default=False)
    points_gained: Mapped[int] = mapped_column(default=0)
    combo_multiplier: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    session: Mapped["GameSession"] = relationship(back_populates="attempts")
