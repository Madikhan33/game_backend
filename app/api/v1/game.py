import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.anomaly_region import AnomalyRegion
from app.models.game_session import GameSession
from app.models.game_attempt import GameAttempt
from app.schemas.game import GameStart, GameAttemptIn, GameAttemptOut, GameSessionOut
from app.utils.geometry import point_in_polygon

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/game", tags=["game"])

MAX_LIVES = 5
BASE_POINTS = 100
COMBO_MULTIPLIERS = {1: 1, 2: 2, 3: 3}


def _found_region_indexes(regions: list[AnomalyRegion], attempts: list[GameAttempt]) -> set[int]:
    found: set[int] = set()
    for previous_attempt in attempts:
        if not previous_attempt.is_hit:
            continue
        for region in regions:
            if region.order_index in found:
                continue
            if point_in_polygon(previous_attempt.x, previous_attempt.y, region.polygon):
                found.add(region.order_index)
                break
    return found


@router.post("/start", response_model=GameSessionOut)
async def start_game(
    data: GameStart,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = GameSession(
        user_id=current_user.id,
        image_set_id=data.image_set_id,
        room_id=data.room_id,
        lives_left=MAX_LIVES,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    logger.info("Game started: session=%s user=%s image_set=%s", session.id, current_user.id, data.image_set_id)
    return session


@router.post("/{session_id}/attempt", response_model=GameAttemptOut)
async def make_attempt(
    session_id: int,
    attempt: GameAttemptIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(GameSession).where(
            GameSession.id == session_id, GameSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.finished_at is not None:
        raise HTTPException(status_code=400, detail="Game already finished")
    if session.lives_left <= 0:
        raise HTTPException(status_code=400, detail="No lives left")

    # Fetch polygon anomaly regions.
    result = await db.execute(
        select(AnomalyRegion).where(AnomalyRegion.image_set_id == session.image_set_id)
    )
    regions = result.scalars().all()
    if not regions:
        raise HTTPException(status_code=400, detail="Image set has no anomaly regions")

    # Fetch previous attempts to avoid double-clicking the same region.
    result = await db.execute(
        select(GameAttempt).where(GameAttempt.session_id == session_id)
    )
    previous_attempts = result.scalars().all()
    found_region_order_indexes = _found_region_indexes(regions, previous_attempts)

    hit = False
    hit_region = None
    for region in regions:
        if region.order_index in found_region_order_indexes:
            continue
        if point_in_polygon(attempt.x, attempt.y, region.polygon):
            hit = True
            hit_region = region
            break

    combo = min(session.max_combo + 1, 3) if hit else 1
    if not hit:
        combo = 1
        session.lives_left -= 1
    else:
        if combo > session.max_combo:
            session.max_combo = combo

    points_gained = BASE_POINTS * COMBO_MULTIPLIERS.get(combo, 1) if hit else 0
    session.total_score += points_gained

    # Activate mutation after 2 hits.
    previous_hits = len([a for a in previous_attempts if a.is_hit])
    if hit and previous_hits + 1 == 2:
        session.mutation_active = True

    db_attempt = GameAttempt(
        session_id=session_id,
        x=attempt.x,
        y=attempt.y,
        is_hit=hit,
        points_gained=points_gained,
        combo_multiplier=combo,
    )
    db.add(db_attempt)

    # Check if all regions are found.
    remaining = [
        region
        for region in regions
        if region.order_index not in found_region_order_indexes and region != hit_region
    ]
    if hit and not remaining:
        from datetime import datetime

        session.finished_at = datetime.utcnow()
        total = len(previous_attempts) + 1
        hits = len([a for a in previous_attempts if a.is_hit]) + (1 if hit else 0)
        session.accuracy_percent = round((hits / total) * 100, 2) if total else 0

    await db.commit()
    await db.refresh(db_attempt)
    await db.refresh(session)
    logger.info(
        "Attempt: session=%s hit=%s points=%s combo=x%s lives=%s",
        session_id, hit, points_gained, combo, session.lives_left
    )
    return db_attempt


@router.get("/{session_id}/state", response_model=GameSessionOut)
async def get_session_state(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(GameSession).where(
            GameSession.id == session_id, GameSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("/{session_id}/finish", response_model=GameSessionOut)
async def finish_game(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(GameSession).where(
            GameSession.id == session_id, GameSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.finished_at is None:
        from datetime import datetime

        session.finished_at = datetime.utcnow()
        result = await db.execute(
            select(GameAttempt).where(GameAttempt.session_id == session_id)
        )
        attempts = result.scalars().all()
        total = len(attempts)
        hits = len([a for a in attempts if a.is_hit])
        session.accuracy_percent = round((hits / total) * 100, 2) if total else 0
        await db.commit()
        await db.refresh(session)
    return session
