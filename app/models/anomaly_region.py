from sqlalchemy import ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AnomalyRegion(Base):
    __tablename__ = "anomaly_regions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    image_set_id: Mapped[int] = mapped_column(ForeignKey("image_sets.id"))
    polygon: Mapped[list[dict[str, float]]] = mapped_column(JSON)
    order_index: Mapped[int] = mapped_column(default=0)

    image_set: Mapped["ImageSet"] = relationship(back_populates="anomaly_regions")
