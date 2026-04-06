from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


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
    secret_key: str = "change-me-in-production-use-openssl-rand-hex-32"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

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
