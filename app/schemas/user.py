from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(UserBase):
    id: int
    avatar_url: str | None = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
