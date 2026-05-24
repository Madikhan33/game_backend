from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.game_session import GameSession
from app.schemas.game import LeaderboardEntry

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("/global", response_model=list[LeaderboardEntry])
async def get_global_leaderboard(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            User.username,
            func.coalesce(func.sum(GameSession.total_score), 0).label("total_score"),
            func.count(GameSession.id).label("games_played"),
        )
        .join(GameSession, User.id == GameSession.user_id)
        .where(GameSession.finished_at.is_not(None))
        .group_by(User.id)
        .order_by(func.sum(GameSession.total_score).desc())
        .limit(50)
    )
    rows = result.all()
    return [
        LeaderboardEntry(
            username=row.username,
            total_score=row.total_score,
            games_played=row.games_played,
        )
        for row in rows
    ]
