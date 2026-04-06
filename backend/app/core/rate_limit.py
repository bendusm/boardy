"""PostgreSQL-based rate limiter for security-critical endpoints.

Uses database for rate limiting to work correctly with multiple workers.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import logging

from fastapi import Request, HTTPException
from sqlmodel import SQLModel, Field, Session, select, delete

from .database import engine
from .ulid import ulid_field
from .config import settings

logger = logging.getLogger(__name__)


# ─── Model ──────────────────────────────────────────────────────────────

class RateLimitEntry(SQLModel, table=True):
    """Rate limit tracking entry."""
    __tablename__ = "rate_limit_entries"

    id: str = Field(default_factory=ulid_field, primary_key=True)
    key: str = Field(index=True)  # IP:endpoint or IP
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        index=True
    )


# ─── Trusted Proxies ────────────────────────────────────────────────────

# Only trust X-Forwarded-For from these IPs (Cloudflare, local)
# In production, populate from settings or Cloudflare's published IP ranges
TRUSTED_PROXY_IPS = {
    "127.0.0.1",
    "::1",
    # Cloudflare IPv4 ranges (subset - full list at cloudflare.com/ips)
    # In production, fetch dynamically or configure via settings
}


def get_client_ip(request: Request) -> str:
    """Extract real client IP, validating X-Forwarded-For only from trusted proxies.

    Security: Prevents IP spoofing by only trusting X-Forwarded-For from known proxies.
    """
    client_ip = request.client.host if request.client else "unknown"

    # Only trust X-Forwarded-For if request came from a trusted proxy
    # In production behind Cloudflare/nginx, the direct client will be the proxy
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        # If we're behind a trusted proxy (or in debug mode), use forwarded IP
        if settings.debug or client_ip in TRUSTED_PROXY_IPS:
            # Take the first (leftmost) IP - the original client
            ip = forwarded.split(",")[0].strip()
            # Basic validation - must look like an IP
            if ip and not ip.startswith("unknown"):
                return ip

    return client_ip


# ─── Rate Limiter ───────────────────────────────────────────────────────

class RateLimiter:
    """PostgreSQL-backed rate limiter that works across multiple workers."""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def _get_key(self, request: Request, key_suffix: Optional[str] = None) -> str:
        """Generate rate limit key from client IP and optional suffix."""
        ip = get_client_ip(request)
        if key_suffix:
            return f"{ip}:{key_suffix}"
        return ip

    def _cleanup_old(self, session: Session, key: str, cutoff: datetime) -> None:
        """Remove entries outside the current window."""
        session.exec(
            delete(RateLimitEntry).where(
                RateLimitEntry.key == key,
                RateLimitEntry.created_at < cutoff
            )
        )

    def is_allowed(self, request: Request, key_suffix: Optional[str] = None) -> bool:
        """Check if request is allowed under rate limit."""
        key = self._get_key(request, key_suffix)
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(seconds=self.window_seconds)

        with Session(engine) as session:
            # Cleanup old entries for this key
            self._cleanup_old(session, key, cutoff)

            # Count recent requests
            count = len(session.exec(
                select(RateLimitEntry).where(
                    RateLimitEntry.key == key,
                    RateLimitEntry.created_at >= cutoff
                )
            ).all())

            if count >= self.max_requests:
                session.commit()  # Commit cleanup
                return False

            # Record this request
            entry = RateLimitEntry(key=key)
            session.add(entry)
            session.commit()
            return True

    def check(self, request: Request, key_suffix: Optional[str] = None) -> None:
        """Raise HTTPException if rate limit exceeded."""
        if not self.is_allowed(request, key_suffix):
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later.",
                headers={"Retry-After": str(self.window_seconds)}
            )


# ─── Cleanup Job ────────────────────────────────────────────────────────

def cleanup_old_entries(max_age_seconds: int = 3600) -> int:
    """Remove rate limit entries older than max_age_seconds.

    Call this periodically (e.g., via cron or background task) to prevent table bloat.
    Returns number of deleted entries.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=max_age_seconds)
    with Session(engine) as session:
        result = session.exec(
            delete(RateLimitEntry).where(RateLimitEntry.created_at < cutoff)
        )
        session.commit()
        deleted = result.rowcount if hasattr(result, 'rowcount') else 0
        logger.info(f"Cleaned up {deleted} old rate limit entries")
        return deleted


# ─── Rate Limiter Instances ─────────────────────────────────────────────

# Rate limiters for different endpoints
token_rate_limiter = RateLimiter(max_requests=10, window_seconds=60)  # 10 req/min
auth_code_rate_limiter = RateLimiter(max_requests=5, window_seconds=60)  # 5 req/min

# Security: Rate limiters for auth endpoints to prevent brute force attacks
login_rate_limiter = RateLimiter(max_requests=5, window_seconds=60)  # 5 login attempts/min
register_rate_limiter = RateLimiter(max_requests=3, window_seconds=60)  # 3 registrations/min
