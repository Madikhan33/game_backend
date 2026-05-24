from datetime import datetime
from typing import List

from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ImageSet(Base):
    __tablename__ = "image_sets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    original_url: Mapped[str] = mapped_column(String(500))
    anomaly_url: Mapped[str] = mapped_column(String(500))
    mutation_type: Mapped[str] = mapped_column(String(50), default="none")  # none | invert | puzzle
    mutation_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    difficulty: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    creator: Mapped["User"] = relationship(back_populates="image_sets")
    anomaly_points: Mapped[List["AnomalyPoint"]] = relationship(
        back_populates="image_set", cascade="all, delete-orphan"
    )
    anomaly_regions: Mapped[List["AnomalyRegion"]] = relationship(
        back_populates="image_set", cascade="all, delete-orphan"
    )
    game_sessions: Mapped[List["GameSession"]] = relationship(
        back_populates="image_set", cascade="all, delete-orphan"
    )
