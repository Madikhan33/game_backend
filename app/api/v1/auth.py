from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, LoginRequest, UserOut, Token
from app.utils.security import get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    result = await db.execute(select(User).where(User.username == user_in.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=Token)
async def login(user_in: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == user_in.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token}


@router.get("/me", response_model=UserOut)
async def read_me(current_user: User = Depends(get_current_user)):
    return current_user
