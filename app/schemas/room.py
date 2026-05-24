from pydantic import BaseModel
from datetime import datetime


class RoomCreate(BaseModel):
    name: str
    max_players: int = 4


class RoomJoin(BaseModel):
    code: str


class RoomPlayerOut(BaseModel):
    id: int
    user_id: int
    username: str | None = None
    status: str
    score: int
    lives_left: int

    class Config:
        from_attributes = True


class RoomOut(BaseModel):
    id: int
    name: str
    code: str
    host_id: int
    image_set_id: int | None = None
    status: str
    max_players: int
    created_at: datetime
    players: list[RoomPlayerOut] = []

    class Config:
        from_attributes = True
