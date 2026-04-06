# Phase 2: FastMCP + OAuth 2.1

Реализуй Phase 2 проекта Boardy согласно спецификации.

## 1. FastMCP Server

Создай `backend/app/mcp_server.py` с FastMCP tools:

```python
# Аннотации обязательны для каталога Anthropic!
@mcp.tool(readOnlyHint=True)
def get_board(board_id: str) -> BoardFull: ...

@mcp.tool(readOnlyHint=True)
def list_boards() -> list[BoardRead]: ...

@mcp.tool(destructiveHint=False)
def create_card(board_id, column_id, title, description=None, priority="medium") -> CardRead: ...

@mcp.tool(destructiveHint=False)
def move_card(card_id, to_column_id, position=0) -> CardRead: ...

@mcp.tool(destructiveHint=False)
def add_comment(card_id, text) -> CommentRead: ...
```

**Критично:**
- Все операции через MCP передают `created_by="claude"`
- Интегрируй MCP сервер в FastAPI на endpoint `/mcp`

## 2. OAuth 2.1 Authorization Server

### Endpoints:
- `GET /.well-known/oauth-authorization-server` — Discovery документ
- `POST /auth/register` — Dynamic Client Registration (RFC 7591)
- `GET /auth/authorize` — Authorization endpoint
- `POST /auth/token` — Token endpoint

### Constraints:
- Callback URL фиксирован: `https://claude.ai/api/mcp/auth_callback`
- PKCE обязателен (code_challenge / code_verifier)
- Токен привязан к конкретному `board_id` через scope или claims
- Использовать Authlib для OAuth 2.1

## 3. Модели

Добавь в `backend/app/auth/models.py`:

```python
class OAuthClient(SQLModel, table=True):
    """Зарегистрированные клиенты (Claude Desktop instances)"""
    id: str = Field(default_factory=ulid_field, primary_key=True)
    client_id: str = Field(unique=True, index=True)
    client_secret: str
    redirect_uris: list[str]  # JSON field
    created_at: datetime

class OAuthToken(SQLModel, table=True):
    """Выданные токены с привязкой к board_id"""
    id: str = Field(default_factory=ulid_field, primary_key=True)
    client_id: str = Field(index=True)
    user_id: str = Field(index=True)
    board_id: str = Field(index=True)  # Claude видит только эту доску
    access_token: str
    refresh_token: str | None
    expires_at: datetime
    created_at: datetime
```

## 4. Миграции

После создания моделей:
```bash
cd backend && alembic revision --autogenerate -m "add oauth models"
cd backend && alembic upgrade head
```

## Checklist

- [ ] FastMCP сервер с 5 tools
- [ ] Все tools имеют `readOnlyHint` или `destructiveHint`
- [ ] OAuth 2.1 discovery endpoint
- [ ] Dynamic Client Registration
- [ ] PKCE support
- [ ] Токен привязан к board_id
- [ ] Миграции созданы и применены
- [ ] `/health` работает
- [ ] MCP endpoint `/mcp` отвечает
