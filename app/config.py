from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./game.db"
    SECRET_KEY: str = "supersecretkey-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    OPENAI_API_KEY: str = ""
    UPLOAD_DIR: str = "static/uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB

    class Config:
        env_file = ".env"


settings = Settings()
