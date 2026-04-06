# Boardy

**SaaS Kanban с нативным MCP-коннектором.**
Пользователь регистрируется, вставляет MCP URL в Claude Desktop — и Claude автоматически ведёт доску.

## Tech Stack

### Backend
- Python 3.12, FastAPI, FastMCP, SQLModel
- Authlib (OAuth 2.1), PostgreSQL 16, Alembic
- Cloudflare R2 (файлы)

### Frontend
- React 18, TypeScript, Vite
- TanStack Query, Zustand
- @hello-pangea/dnd, Tailwind CSS

### Infrastructure
- Docker Compose (local)
- Hetzner CAX11 (prod)
- Nginx, Cloudflare

## Commands

```bash
# Поднять всё локально (postgres + backend + frontend)
docker compose up

# Backend отдельно
cd backend && uvicorn app.main:app --reload

# Frontend отдельно
cd frontend && npm run dev

# Миграции
cd backend && alembic upgrade head           # применить
cd backend && alembic revision --autogenerate -m "description"  # создать

# Тесты
cd backend && pytest -v
```

## Architecture

### API Endpoints
- `/api/v1/auth/*` — регистрация, логин, JWT
- `/api/v1/boards/*` — CRUD досок, колонок, карточек
- `/auth/*` — OAuth 2.1 Authorization Server (Phase 2)
- `/mcp` — FastMCP сервер (Phase 2)
- `/health` — healthcheck

### Key Files
- `backend/app/main.py` — точка входа FastAPI
- `backend/app/mcp_server.py` — FastMCP tools
- `backend/app/auth/oauth_router.py` — OAuth 2.1 Authorization Server
- `backend/app/auth/` — JWT auth + OAuth 2.1 models
- `backend/app/boards/` — основная бизнес-логика
- `frontend/src/pages/Board.tsx` — Kanban UI
- `docker-compose.yml` — local dev окружение

## Development Rules (обязательно соблюдать)

### ID и модели
- Все первичные ключи — **ULID**, не UUID. Использовать `app.core.ulid.ulid_field` как default_factory
- Поле `created_by: enum("user", "claude")` обязательно на моделях Card и Comment
- OAuth токен всегда привязан к конкретному `board_id` — Claude видит только одну доску

### Backend
- Python 3.12, FastAPI, SQLModel (не SQLAlchemy напрямую)
- ORM-сессия только через `Depends(get_session)` — никогда не создавать Session вручную в роутерах
- Бизнес-логика только в `service.py` — роутеры тонкие, только валидация и вызов сервиса
- Миграции только через Alembic — никогда не использовать `create_all()` в продакшне
- Логирование только через `logging` — никаких `print()` в коде
- Переменные окружения только через `app.core.config.settings` (pydantic-settings)
- Без Redis — сессии и rate limit через PostgreSQL

### MCP (критично для попадания в каталог Anthropic)
- Каждый MCP tool обязан иметь аннотацию `readOnlyHint: true` или `destructiveHint: false/true`
- `list_*` и `get_*` инструменты → `readOnlyHint: true`
- `create_*`, `update_*`, `move_*`, `close_*` → `destructiveHint: false`
- `delete_*` → `destructiveHint: true`
- При вызове MCP tools передавать `created_by="claude"` в Card и Comment

### OAuth 2.1
- Callback URL всегда фиксирован: `https://claude.ai/api/mcp/auth_callback`
- Поддержка Dynamic Client Registration (RFC 7591) — эндпоинт `POST /auth/register`
- Discovery документ на `GET /.well-known/oauth-authorization-server`
- PKCE обязателен (code_challenge / code_verifier)

### Frontend
- React 18 + TypeScript (строгий режим)
- Server state через TanStack Query — никакого `useState` для данных с сервера
- Client state через Zustand — только UI-состояние
- Drag & drop через `@hello-pangea/dnd`
- Стили только через Tailwind CSS — никакого inline style и отдельных CSS файлов
- Компоненты в `src/components/`, страницы в `src/pages/`

### Файлы (Phase 3)
- Загрузка файлов через presigned URLs — сервер не буферизует файлы
- Хранилище: Cloudflare R2 (S3-compatible, boto3)

### Git
- Коммиты в формате: `feat:`, `fix:`, `refactor:`, `chore:`
- Перед коммитом убедиться что нет `print()` в backend-коде

## Development Phases

### Phase 1 (done)
- [x] Auth (register, login, JWT)
- [x] Boards CRUD
- [x] Kanban UI с drag-and-drop
- [x] Docker Compose

### Phase 2 (done)
- [x] FastMCP сервер с tools: list_boards, get_board, create_card, update_card, move_card, add_comment, attach_file, close_card
- [x] OAuth 2.1 Authorization Server
- [x] Dynamic Client Registration (RFC 7591)
- [x] MCP token exchange flow с PKCE

### Phase 3 (future)
- [ ] Файлы через Cloudflare R2
- [ ] close_card tool
- [ ] Deploy на Hetzner CAX11

## MCP Tools (Phase 2)

При реализации FastMCP сервера, создать tools с обязательными аннотациями:

| Tool | Hint | Описание |
|------|------|----------|
| `get_board(board_id)` | `readOnlyHint: true` | Полная доска с колонками и карточками |
| `list_boards()` | `readOnlyHint: true` | Список досок текущего пользователя |
| `create_card(board_id, column_id, title, description?, priority?)` | `destructiveHint: false` | Создать карточку |
| `move_card(card_id, to_column_id, position?)` | `destructiveHint: false` | Переместить карточку |
| `add_comment(card_id, text)` | `destructiveHint: false` | Добавить комментарий |
| `close_card(card_id)` (Phase 3) | `destructiveHint: false` | Закрыть карточку |

Все операции через MCP должны иметь `created_by: "claude"`.
