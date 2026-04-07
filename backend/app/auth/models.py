from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional
from app.core.ulid import ulid_field


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=ulid_field, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: Optional[str] = None  # display name
    hashed_password: Optional[str] = None  # Optional for social auth users
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    terms_accepted_at: Optional[datetime] = None  # GDPR: when user accepted Terms & Privacy Policy

    # Social auth providers
    github_id: Optional[str] = Field(default=None, unique=True, index=True)
    google_id: Optional[str] = Field(default=None, unique=True, index=True)

    # Serializable representation (без пароля)
    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name or self.email.split("@")[0],
            "created_at": self.created_at.isoformat(),
        }


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
    board_id: str          # primary board (first authorized)
    allowed_board_ids: Optional[str] = None  # JSON array of all allowed board IDs
    access_token: str = Field(unique=True, index=True)
    refresh_token: Optional[str] = Field(default=None, unique=True, index=True)
    scope: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def get_board_ids(self) -> list[str]:
        """Get all allowed board IDs."""
        if self.allowed_board_ids:
            import json
            return json.loads(self.allowed_board_ids)
        return [self.board_id]

    def set_board_ids(self, board_ids: list[str]) -> None:
        """Set allowed board IDs."""
        import json
        self.allowed_board_ids = json.dumps(board_ids)


class TokenBlacklist(SQLModel, table=True):
    """Blacklisted JWT tokens for logout invalidation.

    Security: Stores invalidated tokens until they would have expired naturally.
    Should be cleaned up periodically to remove expired entries.
    """
    __tablename__ = "token_blacklist"

    id: str = Field(default_factory=ulid_field, primary_key=True)
    token_jti: str = Field(unique=True, index=True)  # JWT ID or hash of token
    user_id: str = Field(index=True)
    expires_at: datetime  # When this token would have expired
    blacklisted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
