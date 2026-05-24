import logging
import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.image import ImageSet
from app.models.game_room import GameRoom, RoomPlayer
from app.schemas.room import RoomCreate, RoomJoin, RoomOut, RoomPlayerOut

logger = logging.getLogger(__name__)


async def get_room_with_players(db: AsyncSession, room_id: int):
    result = await db.execute(
        select(GameRoom)
        .options(selectinload(GameRoom.players).selectinload(RoomPlayer.user))
        .where(GameRoom.id == room_id)
    )
    return result.scalar_one_or_none()

router = APIRouter(prefix="/rooms", tags=["rooms"])


def generate_code() -> str:
    return secrets.token_urlsafe(6)[:8].upper()


@router.post("", response_model=RoomOut)
async def create_room(
    data: RoomCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    room = GameRoom(
        name=data.name,
        code=generate_code(),
        host_id=current_user.id,
        max_players=data.max_players,
    )
    db.add(room)
    await db.commit()
    await db.refresh(room)

    player = RoomPlayer(room_id=room.id, user_id=current_user.id)
    db.add(player)
    await db.commit()

    result = await db.execute(
        select(GameRoom).options(selectinload(GameRoom.players).selectinload(RoomPlayer.user)).where(GameRoom.id == room.id)
    )
    logger.info("Room created: id=%s code=%s host=%s", room.id, room.code, current_user.id)
    return result.scalar_one()


@router.post("/join", response_model=RoomOut)
async def join_room(
    data: RoomJoin,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(GameRoom).options(selectinload(GameRoom.players).selectinload(RoomPlayer.user)).where(GameRoom.code == data.code))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if room.status != "waiting":
        raise HTTPException(status_code=400, detail="Game already started")

    result = await db.execute(
        select(RoomPlayer).where(
            RoomPlayer.room_id == room.id, RoomPlayer.user_id == current_user.id
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        return room

    result = await db.execute(select(RoomPlayer).where(RoomPlayer.room_id == room.id))
    players = result.scalars().all()
    if len(players) >= room.max_players:
        raise HTTPException(status_code=400, detail="Room is full")

    player = RoomPlayer(room_id=room.id, user_id=current_user.id)
    db.add(player)
    await db.commit()

    result = await db.execute(
        select(GameRoom).options(selectinload(GameRoom.players).selectinload(RoomPlayer.user)).where(GameRoom.id == room.id)
    )
    logger.info("User %s joined room %s", current_user.id, room.id)
    return result.scalar_one()


@router.get("/{room_id}", response_model=RoomOut)
async def get_room(room_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GameRoom).options(selectinload(GameRoom.players).selectinload(RoomPlayer.user)).where(GameRoom.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.post("/{room_id}/start", response_model=RoomOut)
async def start_room_game(
    room_id: int,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image_set_id = data.get("image_set_id")
    result = await db.execute(select(GameRoom).options(selectinload(GameRoom.players).selectinload(RoomPlayer.user)).where(GameRoom.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if room.host_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only host can start")

    result = await db.execute(select(ImageSet).where(ImageSet.id == image_set_id))
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(status_code=404, detail="Image set not found")

    room.image_set_id = image_set_id
    room.status = "playing"
    await db.commit()

    result = await db.execute(
        select(GameRoom).options(selectinload(GameRoom.players).selectinload(RoomPlayer.user)).where(GameRoom.id == room.id)
    )
    logger.info("Room %s started game with image_set %s", room.id, image_set_id)
    return result.scalar_one()


@router.post("/{room_id}/finish", response_model=RoomOut)
async def finish_room_game(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(GameRoom).options(selectinload(GameRoom.players).selectinload(RoomPlayer.user)).where(GameRoom.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if room.host_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only host can finish")
    room.status = "finished"
    await db.commit()

    result = await db.execute(
        select(GameRoom).options(selectinload(GameRoom.players).selectinload(RoomPlayer.user)).where(GameRoom.id == room.id)
    )
    return result.scalar_one()
