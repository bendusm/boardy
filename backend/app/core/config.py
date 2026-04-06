from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from functools import lru_cache
import secrets


# Placeholder that MUST be replaced in production
_INSECURE_SECRET_PLACEHOLDER = "change-me-in-production-use-openssl-rand-hex-32"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_name: str = "Boardy"
    app_url: str = "https://boardy.alivik.io"
    debug: bool = False

    # Database
    database_url: str = "postgresql://boardy:boardy@localhost:5432/boardy"

    # JWT
    secret_key: str = _INSECURE_SECRET_PLACEHOLDER
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60  # 1 hour (was 7 days - insecure)

    @model_validator(mode="after")
    def validate_secret_key(self):
        """Reject insecure placeholder secret in production."""
        if not self.debug and self.secret_key == _INSECURE_SECRET_PLACEHOLDER:
            raise ValueError(
                "SECURITY ERROR: secret_key must be set in production! "
                "Generate one with: openssl rand -hex 32"
            )
        if len(self.secret_key) < 32:
            raise ValueError("secret_key must be at least 32 characters")
        return self

    # OAuth
    oauth_auth_code_expire_seconds: int = 300  # 5 min
    oauth_access_token_expire_seconds: int = 3600  # 1 hour
    oauth_refresh_token_expire_days: int = 30

    # Cloudflare R2
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = "boardy"
    r2_public_url: str = ""  # e.g. https://files.boardy.app

    # MCP
    mcp_server_url: str = "https://boardy.alivik.io/mcp"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
