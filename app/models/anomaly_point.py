from sqlalchemy import ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AnomalyPoint(Base):
    __tablename__ = "anomaly_points"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    image_set_id: Mapped[int] = mapped_column(ForeignKey("image_sets.id"))
    x: Mapped[float] = mapped_column(Float)
    y: Mapped[float] = mapped_column(Float)
    radius: Mapped[float] = mapped_column(Float, default=20.0)
    order_index: Mapped[int] = mapped_column(default=0)

    image_set: Mapped["ImageSet"] = relationship(back_populates="anomaly_points")
