from pydantic import BaseModel
from datetime import datetime


class GameStart(BaseModel):
    image_set_id: int
    room_id: int | None = None


class GameAttemptIn(BaseModel):
    x: float
    y: float


class GameAttemptOut(GameAttemptIn):
    id: int
    session_id: int
    is_hit: bool
    points_gained: int
    combo_multiplier: int
    created_at: datetime

    class Config:
        from_attributes = True


class GameSessionOut(BaseModel):
    id: int
    user_id: int
    image_set_id: int
    room_id: int | None = None
    started_at: datetime
    finished_at: datetime | None = None
    total_score: int
    max_combo: int
    accuracy_percent: float
    lives_left: int
    mutation_active: bool

    class Config:
        from_attributes = True


class LeaderboardEntry(BaseModel):
    username: str
    total_score: int
    games_played: int
