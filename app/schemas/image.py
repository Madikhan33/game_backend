from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PolygonPoint(BaseModel):
    x: float
    y: float


class AnomalyRegionCreate(BaseModel):
    polygon: list[PolygonPoint] = Field(min_length=3)
    order_index: int = 0

    @field_validator("polygon")
    @classmethod
    def polygon_must_have_three_points(cls, value: list[PolygonPoint]) -> list[PolygonPoint]:
        if len(value) < 3:
            raise ValueError("Polygon requires at least 3 points")
        return value


class AnomalyRegionOut(AnomalyRegionCreate):
    id: int
    image_set_id: int

    model_config = ConfigDict(from_attributes=True)


class ImageSetCreate(BaseModel):
    title: str
    description: str | None = None
    mutation_type: str = "none"
    mutation_config: dict | None = None
    difficulty: int = 1


class ImageSetOut(ImageSetCreate):
    id: int
    original_url: str
    anomaly_url: str
    creator_id: int
    creator_username: str | None = None
    created_at: datetime
    anomaly_regions: list[AnomalyRegionOut] = []

    model_config = ConfigDict(from_attributes=True)
