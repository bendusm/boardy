from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse
from sqlmodel import Session
from pydantic import BaseModel, EmailStr
import secrets
import json
import re

from app.core.database import get_session
from app.core.deps import get_current_user
from app.core.config import settings
from app.core.rate_limit import login_rate_limiter, register_rate_limiter
from .models import User
from .service import authenticate_user, create_user, create_access_token, get_user_by_email, blacklist_token


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password complexity.

    Security: Requires minimum length, uppercase, lowercase, digit, and special char.
    Returns (is_valid, error_message).
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)"
    return True, ""

router = APIRouter()

# Cookie settings
COOKIE_NAME = "boardy_session"
CSRF_COOKIE_NAME = "boardy_csrf"
COOKIE_MAX_AGE = settings.access_token_expire_minutes * 60  # seconds


def set_auth_cookies(response: Response, token: str) -> str:
    """Set httpOnly session cookie and CSRF cookie. Returns CSRF token."""
    csrf_token = secrets.token_urlsafe(32)

    # Session cookie - httpOnly, not accessible from JS
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        secure=not settings.debug,  # HTTPS only in production
        samesite="lax",
        path="/",
    )

    # CSRF cookie - readable by JS for header inclusion
    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=csrf_token,
        max_age=COOKIE_MAX_AGE,
        httponly=False,  # JS needs to read this
        secure=not settings.debug,
        samesite="lax",
        path="/",
    )

    return csrf_token


def clear_auth_cookies(response: Response) -> None:
    """Clear auth cookies on logout."""
    response.delete_cookie(key=COOKIE_NAME, path="/")
    response.delete_cookie(key=CSRF_COOKIE_NAME, path="/")


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    user: dict
    csrf_token: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, request: Request, session: Session = Depends(get_session)):
    # Security: Rate limit registration to prevent abuse
    register_rate_limiter.check(request)

    if get_user_by_email(session, body.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Security: Validate password complexity
    is_valid, error_msg = validate_password(body.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    user = create_user(session, email=body.email, password=body.password)
    token = create_access_token(user.id)

    response = Response(media_type="application/json", status_code=status.HTTP_201_CREATED)
    csrf_token = set_auth_cookies(response, token)
    body = json.dumps({"user": user.to_dict(), "csrf_token": csrf_token})
    response.body = body.encode()
    response.headers["content-length"] = str(len(response.body))
    return response


@router.post("/login")
def login(body: LoginRequest, request: Request, session: Session = Depends(get_session)):
    # Security: Rate limit login to prevent brute force attacks
    login_rate_limiter.check(request)

    user = authenticate_user(session, email=body.email, password=body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    token = create_access_token(user.id)

    # Create response with placeholder, set cookies, then rebuild with correct content
    response = Response(media_type="application/json")
    csrf_token = set_auth_cookies(response, token)
    body = json.dumps({"user": user.to_dict(), "csrf_token": csrf_token})
    response.body = body.encode()
    response.headers["content-length"] = str(len(response.body))
    return response


@router.post("/logout")
def logout(
    request: Request,
    session: Session = Depends(get_session),
):
    """Clear auth cookies and invalidate token.

    Security: Blacklists the token so it cannot be reused even if intercepted.
    """
    # Get token from cookie
    token = request.cookies.get(COOKIE_NAME)
    if token:
        # Decode to get user_id for blacklist entry
        try:
            from jose import jwt
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            user_id = payload.get("sub")
            if user_id:
                blacklist_token(session, token, user_id)
        except Exception:
            pass  # Invalid token - nothing to blacklist

    response = JSONResponse(content={"ok": True})
    clear_auth_cookies(response)
    return response


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return current_user.to_dict()
