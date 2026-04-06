from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from jose import JWTError, jwt

from .database import get_session
from .config import settings

bearer_scheme = HTTPBearer(auto_error=False)

# Cookie name must match router.py
COOKIE_NAME = "boardy_session"
CSRF_HEADER = "X-CSRF-Token"
CSRF_COOKIE = "boardy_csrf"


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_session),
):
    """Authenticate user from cookie (preferred) or Bearer token (fallback)."""
    from app.auth.models import User  # avoid circular import

    token = None

    # 1. Try httpOnly cookie first (more secure)
    cookie_token = request.cookies.get(COOKIE_NAME)
    if cookie_token:
        # Verify CSRF token for state-changing requests
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            csrf_header = request.headers.get(CSRF_HEADER)
            csrf_cookie = request.cookies.get(CSRF_COOKIE)
            if not csrf_header or not csrf_cookie or csrf_header != csrf_cookie:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid or missing CSRF token",
                )
        token = cookie_token

    # 2. Fall back to Bearer token (for API clients, MCP, etc.)
    if not token and credentials:
        token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        jti: str = payload.get("jti")
        if not user_id:
            raise ValueError("No sub in token")

        # Security: Check if token has been blacklisted (logout)
        if jti:
            from app.auth.service import is_token_blacklisted
            if is_token_blacklisted(session, jti):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked",
                    headers={"WWW-Authenticate": "Bearer"},
                )
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
