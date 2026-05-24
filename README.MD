# Anomaly Hunt — Backend

FastAPI backend для игры "Найди аномалию".

## Стек
- FastAPI + async SQLAlchemy 2.0 + SQLite (aiosqlite)
- Argon2 для хеширования паролей
- JWT авторизация
- OpenAI API для генерации аномалий
- Granian ASGI сервер

## Запуск

```bash
# Установка зависимостей
uv sync

# Запуск сервера
uv run granian --interface asgi main:app --port 8000
```

## Переменные окружения (.env)
```env
DATABASE_URL=sqlite+aiosqlite:///./game.db
SECRET_KEY=supersecretkey-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENAI_API_KEY=sk-...
UPLOAD_DIR=static/uploads
```

## API Endpoints

### Auth
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

### Images (Levels)
- `POST /api/v1/images` — загрузка оригинала и аномалии
- `POST /api/v1/images/{id}/anomaly-regions` — полигональная разметка аномалий
- `GET /api/v1/images` — список уровней

### Game
- `POST /api/v1/game/start`
- `POST /api/v1/game/{session_id}/attempt`
- `GET /api/v1/game/{session_id}/state`
- `POST /api/v1/game/{session_id}/finish`

### Rooms (Multiplayer)
- `POST /api/v1/rooms`
- `POST /api/v1/rooms/join`
- `GET /api/v1/rooms/{id}`
- `POST /api/v1/rooms/{id}/start`

### WebSocket
- `WS /ws/rooms/{room_id}`
