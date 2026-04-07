"""Social OAuth authentication (GitHub, Google) for Boardy."""

import secrets
import logging
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.config import settings
from .models import User
from .router import set_auth_cookies
from .service import create_access_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/social", tags=["social-auth"])

# In-memory state storage (use Redis in production for multi-instance)
_oauth_states: dict[str, dict] = {}


def _generate_state() -> str:
    """Generate a secure random state parameter."""
    return secrets.token_urlsafe(32)


def _store_state(state: str, data: dict) -> None:
    """Store OAuth state data."""
    _oauth_states[state] = {**data, "created_at": datetime.now(timezone.utc)}


def _verify_state(state: str) -> dict | None:
    """Verify and consume OAuth state."""
    data = _oauth_states.pop(state, None)
    if not data:
        return None
    # State expires after 10 minutes
    created_at = data.get("created_at")
    if created_at and (datetime.now(timezone.utc) - created_at).seconds > 600:
        return None
    return data


# ─── GitHub OAuth ───────────────────────────────────────────────────


@router.get("/github")
def github_login(
    oauth_client_id: Optional[str] = Query(None),
    oauth_redirect_uri: Optional[str] = Query(None),
    oauth_response_type: Optional[str] = Query(None),
    oauth_state: Optional[str] = Query(None),
    oauth_scope: Optional[str] = Query(None),
    oauth_code_challenge: Optional[str] = Query(None),
    oauth_code_challenge_method: Optional[str] = Query(None),
):
    """Redirect to GitHub OAuth authorization."""
    if not settings.github_client_id:
        raise HTTPException(status_code=503, detail="GitHub OAuth not configured")

    state = _generate_state()
    state_data = {"provider": "github"}

    # Preserve MCP OAuth flow params if present
    if oauth_client_id:
        state_data["oauth_flow"] = {
            "client_id": oauth_client_id,
            "redirect_uri": oauth_redirect_uri,
            "response_type": oauth_response_type,
            "state": oauth_state,
            "scope": oauth_scope,
            "code_challenge": oauth_code_challenge,
            "code_challenge_method": oauth_code_challenge_method,
        }

    _store_state(state, state_data)

    params = {
        "client_id": settings.github_client_id,
        "redirect_uri": f"{settings.app_url}/api/v1/auth/social/github/callback",
        "scope": "read:user user:email",
        "state": state,
    }
    return RedirectResponse(f"https://github.com/login/oauth/authorize?{urlencode(params)}")


@router.get("/github/callback")
def github_callback(
    code: str = Query(...),
    state: str = Query(...),
    session: Session = Depends(get_session),
):
    """Handle GitHub OAuth callback."""
    # Verify state
    state_data = _verify_state(state)
    if not state_data or state_data.get("provider") != "github":
        raise HTTPException(status_code=400, detail="Invalid or expired state")

    # Exchange code for access token
    token_response = httpx.post(
        "https://github.com/login/oauth/access_token",
        data={
            "client_id": settings.github_client_id,
            "client_secret": settings.github_client_secret,
            "code": code,
            "redirect_uri": f"{settings.app_url}/api/v1/auth/social/github/callback",
        },
        headers={"Accept": "application/json"},
        timeout=10,
    )

    if token_response.status_code != 200:
        logger.error(f"GitHub token exchange failed: {token_response.text}")
        raise HTTPException(status_code=400, detail="Failed to authenticate with GitHub")

    token_data = token_response.json()
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token from GitHub")

    # Get user info from GitHub
    user_response = httpx.get(
        "https://api.github.com/user",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        },
        timeout=10,
    )

    if user_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get GitHub user info")

    github_user = user_response.json()
    github_id = str(github_user["id"])

    # Get primary email if not public
    email = github_user.get("email")
    if not email:
        emails_response = httpx.get(
            "https://api.github.com/user/emails",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
            timeout=10,
        )
        if emails_response.status_code == 200:
            emails = emails_response.json()
            primary = next((e for e in emails if e.get("primary")), None)
            email = primary["email"] if primary else emails[0]["email"] if emails else None

    if not email:
        raise HTTPException(status_code=400, detail="Could not get email from GitHub")

    # Find or create user
    user = session.exec(select(User).where(User.github_id == github_id)).first()

    if not user:
        # Check if email already exists
        user = session.exec(select(User).where(User.email == email)).first()
        if user:
            # Link GitHub to existing account
            user.github_id = github_id
            if not user.name and github_user.get("name"):
                user.name = github_user["name"]
        else:
            # Create new user
            user = User(
                email=email,
                name=github_user.get("name") or github_user.get("login"),
                github_id=github_id,
                terms_accepted_at=datetime.now(timezone.utc),
            )
            session.add(user)

        session.commit()
        session.refresh(user)

    # Create JWT and set cookies
    token = create_access_token(user.id)

    # If this was part of an MCP OAuth flow, redirect back to authorize with user context
    oauth_flow = state_data.get("oauth_flow")
    if oauth_flow and oauth_flow.get("client_id"):
        from .oauth_router import create_session_token
        session_token = create_session_token(user.id)
        redirect_params = {
            "client_id": oauth_flow["client_id"],
            "redirect_uri": oauth_flow["redirect_uri"],
            "response_type": oauth_flow["response_type"],
            "state": oauth_flow["state"],
            "scope": oauth_flow["scope"],
            "code_challenge": oauth_flow["code_challenge"],
            "code_challenge_method": oauth_flow["code_challenge_method"],
            "user_id": user.id,
            "session_token": session_token,
        }
        response = RedirectResponse(
            url=f"{settings.app_url}/auth/authorize/select-board?{urlencode(redirect_params)}",
            status_code=302,
        )
        set_auth_cookies(response, token)
        logger.info(f"GitHub login successful for user {user.id} (MCP OAuth flow)")
        return response

    response = RedirectResponse(url=f"{settings.app_url}/dashboard", status_code=302)
    set_auth_cookies(response, token)

    logger.info(f"GitHub login successful for user {user.id}")
    return response


# ─── Google OAuth ───────────────────────────────────────────────────


@router.get("/google")
def google_login(
    oauth_client_id: Optional[str] = Query(None),
    oauth_redirect_uri: Optional[str] = Query(None),
    oauth_response_type: Optional[str] = Query(None),
    oauth_state: Optional[str] = Query(None),
    oauth_scope: Optional[str] = Query(None),
    oauth_code_challenge: Optional[str] = Query(None),
    oauth_code_challenge_method: Optional[str] = Query(None),
):
    """Redirect to Google OAuth authorization."""
    if not settings.google_client_id:
        raise HTTPException(status_code=503, detail="Google OAuth not configured")

    state = _generate_state()
    state_data = {"provider": "google"}

    # Preserve MCP OAuth flow params if present
    if oauth_client_id:
        state_data["oauth_flow"] = {
            "client_id": oauth_client_id,
            "redirect_uri": oauth_redirect_uri,
            "response_type": oauth_response_type,
            "state": oauth_state,
            "scope": oauth_scope,
            "code_challenge": oauth_code_challenge,
            "code_challenge_method": oauth_code_challenge_method,
        }

    _store_state(state, state_data)

    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": f"{settings.app_url}/api/v1/auth/social/google/callback",
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "select_account",
    }
    return RedirectResponse(f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}")


@router.get("/google/callback")
def google_callback(
    code: str = Query(...),
    state: str = Query(...),
    session: Session = Depends(get_session),
):
    """Handle Google OAuth callback."""
    # Verify state
    state_data = _verify_state(state)
    if not state_data or state_data.get("provider") != "google":
        raise HTTPException(status_code=400, detail="Invalid or expired state")

    # Exchange code for tokens
    token_response = httpx.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "code": code,
            "redirect_uri": f"{settings.app_url}/api/v1/auth/social/google/callback",
            "grant_type": "authorization_code",
        },
        timeout=10,
    )

    if token_response.status_code != 200:
        logger.error(f"Google token exchange failed: {token_response.text}")
        raise HTTPException(status_code=400, detail="Failed to authenticate with Google")

    token_data = token_response.json()
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token from Google")

    # Get user info from Google
    user_response = httpx.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )

    if user_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get Google user info")

    google_user = user_response.json()
    google_id = google_user["id"]
    email = google_user.get("email")

    if not email:
        raise HTTPException(status_code=400, detail="Could not get email from Google")

    # Find or create user
    user = session.exec(select(User).where(User.google_id == google_id)).first()

    if not user:
        # Check if email already exists
        user = session.exec(select(User).where(User.email == email)).first()
        if user:
            # Link Google to existing account
            user.google_id = google_id
            if not user.name and google_user.get("name"):
                user.name = google_user["name"]
        else:
            # Create new user
            user = User(
                email=email,
                name=google_user.get("name"),
                google_id=google_id,
                terms_accepted_at=datetime.now(timezone.utc),
            )
            session.add(user)

        session.commit()
        session.refresh(user)

    # Create JWT and set cookies
    token = create_access_token(user.id)

    # If this was part of an MCP OAuth flow, redirect back to authorize with user context
    oauth_flow = state_data.get("oauth_flow")
    if oauth_flow and oauth_flow.get("client_id"):
        from .oauth_router import create_session_token
        session_token = create_session_token(user.id)
        redirect_params = {
            "client_id": oauth_flow["client_id"],
            "redirect_uri": oauth_flow["redirect_uri"],
            "response_type": oauth_flow["response_type"],
            "state": oauth_flow["state"],
            "scope": oauth_flow["scope"],
            "code_challenge": oauth_flow["code_challenge"],
            "code_challenge_method": oauth_flow["code_challenge_method"],
            "user_id": user.id,
            "session_token": session_token,
        }
        response = RedirectResponse(
            url=f"{settings.app_url}/auth/authorize/select-board?{urlencode(redirect_params)}",
            status_code=302,
        )
        set_auth_cookies(response, token)
        logger.info(f"Google login successful for user {user.id} (MCP OAuth flow)")
        return response

    response = RedirectResponse(url=f"{settings.app_url}/dashboard", status_code=302)
    set_auth_cookies(response, token)

    logger.info(f"Google login successful for user {user.id}")
    return response
