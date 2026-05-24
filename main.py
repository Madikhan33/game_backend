import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.api.v1 import auth, images, game, rooms, leaderboard, openai
from app.api import websocket

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="Anomaly Game API", lifespan=lifespan)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000
    logger.info(
        "%s %s %s - %.2fms",
        request.method,
        request.url.path,
        response.status_code,
        duration,
    )
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router, prefix="/api/v1")
app.include_router(images.router, prefix="/api/v1")
app.include_router(game.router, prefix="/api/v1")
app.include_router(rooms.router, prefix="/api/v1")
app.include_router(leaderboard.router, prefix="/api/v1")
app.include_router(openai.router, prefix="/api/v1")
app.include_router(websocket.router)


if __name__ == "__main__":
    import subprocess
    import sys

    subprocess.run(
        [
            sys.executable, "-m", "granian",
            "--interface", "asgi",
            "main:app",
            "--port", "8000",
        ]
    )
