from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional
from app.core.ulid import ulid_field


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=ulid_field, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Serializable representation (без пароля)
    def to_dict(self):
        return {"id": self.id, "email": self.email, "created_at": self.created_at.isoformat()}


# ─── OAuth 2.1 models ───────────────────────────────────────────────

class OAuthClient(SQLModel, table=True):
    __tablename__ = "oauth_clients"

    id: str = Field(default_factory=ulid_field, primary_key=True)
    client_id: str = Field(unique=True, index=True)
    client_secret: str
    client_name: str = ""
    redirect_uris: str = ""          # JSON array stored as text
    scope: str = "board:read board:write"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OAuthAuthCode(SQLModel, table=True):
    """Temporary auth codes exchanged for tokens (5 min TTL)."""
    __tablename__ = "oauth_auth_codes"

    id: str = Field(default_factory=ulid_field, primary_key=True)
    code: str = Field(unique=True, index=True)
    client_id: str = Field(index=True)
    user_id: str = Field(index=True)
    board_id: str
    scope: str
    redirect_uri: str
    code_challenge: Optional[str] = None
    code_challenge_method: Optional[str] = None  # Always "S256" for OAuth 2.1
    expires_at: datetime
    used: bool = False


class OAuthToken(SQLModel, table=True):
    __tablename__ = "oauth_tokens"

    id: str = Field(default_factory=ulid_field, primary_key=True)
    client_id: str = Field(index=True)
    user_id: str = Field(index=True)
    board_id: str          # токен привязан к одной доске
    access_token: str = Field(unique=True, index=True)
    refresh_token: Optional[str] = Field(default=None, unique=True, index=True)
    scope: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
