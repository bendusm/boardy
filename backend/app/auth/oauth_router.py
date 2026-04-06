"""OAuth 2.1 Authorization Server for Boardy MCP integration."""

from datetime import datetime, timedelta, timezone
from typing import Optional
import secrets
import hashlib
import base64
import json
import logging

from fastapi import APIRouter, Depends, Form, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.config import settings
from .models import OAuthClient, OAuthAuthCode, OAuthToken, User
from .service import authenticate_user
from app.boards.service import get_boards, get_board

logger = logging.getLogger(__name__)

# ─── Routers ────────────────────────────────────────────────────────────

discovery_router = APIRouter()  # Mounted at app root
oauth_router = APIRouter()      # Mounted at /auth


# ─── Pydantic Models ────────────────────────────────────────────────────

class ClientRegistrationRequest(BaseModel):
    client_name: str
    redirect_uris: list[str]


class ClientRegistrationResponse(BaseModel):
    client_id: str
    client_secret: str
    client_name: str
    redirect_uris: list[str]
    scope: str
    grant_types: list[str] = ["authorization_code", "refresh_token"]
    response_types: list[str] = ["code"]
    token_endpoint_auth_method: str = "client_secret_post"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    scope: str


# ─── HTML Templates ─────────────────────────────────────────────────────

LOGIN_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Boardy - Sign In</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,wght@1,400;1,600;1,700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            min-height: 100vh;
            background: #fafaf9;
            color: #1a1c1b;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }}
        .header {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 40px;
            margin-top: 40px;
        }}
        .logo {{
            width: 32px;
            height: 32px;
            background: #c24e2c;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .logo svg {{ width: 20px; height: 20px; color: white; }}
        .brand {{
            font-family: 'Newsreader', serif;
            font-style: italic;
            font-size: 24px;
            font-weight: 700;
            color: #1a1c1b;
        }}
        .card {{
            background: white;
            padding: 40px;
            border-radius: 24px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.04), 0 0 1px rgba(0,0,0,0.1);
            border: 1px solid rgba(219, 193, 185, 0.1);
            width: 100%;
            max-width: 420px;
        }}
        h2 {{
            font-family: 'Newsreader', serif;
            font-style: italic;
            font-size: 32px;
            font-weight: 400;
            margin-bottom: 8px;
            color: #1a1c1b;
        }}
        .subtitle {{
            color: #645d56;
            margin-bottom: 32px;
            font-size: 15px;
            line-height: 1.5;
        }}
        .subtitle strong {{ color: #c24e2c; }}
        label {{
            display: block;
            font-size: 14px;
            font-weight: 600;
            color: #1a1c1b;
            margin-bottom: 8px;
        }}
        input[type="email"], input[type="password"] {{
            width: 100%;
            padding: 14px 16px;
            margin-bottom: 20px;
            border: 1px solid rgba(219, 193, 185, 0.3);
            border-radius: 12px;
            font-size: 15px;
            font-family: 'Plus Jakarta Sans', sans-serif;
            background: #f4f3f1;
            transition: all 0.2s;
        }}
        input:focus {{
            outline: none;
            border-color: #c24e2c;
            box-shadow: 0 0 0 3px rgba(194, 78, 44, 0.15);
            background: white;
        }}
        input::placeholder {{ color: #88726c; }}
        button {{
            width: 100%;
            padding: 16px;
            background: #c24e2c;
            color: white;
            border: none;
            border-radius: 50px;
            font-size: 16px;
            font-weight: 700;
            font-family: 'Plus Jakarta Sans', sans-serif;
            cursor: pointer;
            transition: all 0.2s;
            margin-top: 8px;
        }}
        button:hover {{
            box-shadow: 0 8px 20px rgba(194, 78, 44, 0.3);
            transform: scale(1.02);
        }}
        .error {{
            background: #fef2f2;
            color: #dc2626;
            padding: 14px 16px;
            border-radius: 12px;
            margin-bottom: 20px;
            font-size: 14px;
            border: 1px solid #fecaca;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
            </svg>
        </div>
        <span class="brand">Boardy</span>
    </div>
    <div class="card">
        <h2>Welcome back</h2>
        <p class="subtitle"><strong>{client_name}</strong> wants to access your boards</p>
        {error_html}
        <form method="POST">
            <input type="hidden" name="client_id" value="{client_id}">
            <input type="hidden" name="redirect_uri" value="{redirect_uri}">
            <input type="hidden" name="response_type" value="{response_type}">
            <input type="hidden" name="state" value="{state}">
            <input type="hidden" name="scope" value="{scope}">
            <input type="hidden" name="code_challenge" value="{code_challenge}">
            <input type="hidden" name="code_challenge_method" value="{code_challenge_method}">
            <label for="email">Email</label>
            <input type="email" id="email" name="email" placeholder="you@example.com" required>
            <label for="password">Password</label>
            <input type="password" id="password" name="password" placeholder="••••••••" required>
            <button type="submit">Sign in</button>
        </form>
    </div>
</body>
</html>"""

BOARD_SELECTION_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Boardy - Authorize</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,wght@1,400;1,600;1,700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            min-height: 100vh;
            background: #fafaf9;
            color: #1a1c1b;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }}
        .header {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 40px;
            margin-top: 40px;
        }}
        .logo {{
            width: 32px;
            height: 32px;
            background: #c24e2c;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .logo svg {{ width: 20px; height: 20px; color: white; }}
        .brand {{
            font-family: 'Newsreader', serif;
            font-style: italic;
            font-size: 24px;
            font-weight: 700;
            color: #1a1c1b;
        }}
        .card {{
            background: white;
            padding: 40px;
            border-radius: 24px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.04), 0 0 1px rgba(0,0,0,0.1);
            border: 1px solid rgba(219, 193, 185, 0.1);
            width: 100%;
            max-width: 480px;
        }}
        h2 {{
            font-family: 'Newsreader', serif;
            font-style: italic;
            font-size: 32px;
            font-weight: 400;
            margin-bottom: 8px;
            color: #1a1c1b;
        }}
        .scope {{
            color: #645d56;
            margin-bottom: 28px;
            font-size: 14px;
        }}
        .scope code {{
            background: #ffdbd0;
            color: #7a2f15;
            padding: 4px 10px;
            border-radius: 20px;
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 12px;
            font-weight: 600;
        }}
        h3 {{
            font-size: 14px;
            font-weight: 600;
            color: #1a1c1b;
            margin-bottom: 16px;
        }}
        .board-option {{
            display: flex;
            align-items: center;
            padding: 18px 20px;
            border: 2px solid rgba(219, 193, 185, 0.3);
            margin-bottom: 12px;
            border-radius: 16px;
            cursor: pointer;
            transition: all 0.2s;
            background: #fafaf9;
        }}
        .board-option:hover {{
            border-color: #c24e2c;
            background: white;
        }}
        .board-option input[type="radio"] {{
            width: 20px;
            height: 20px;
            margin-right: 14px;
            accent-color: #c24e2c;
        }}
        .board-name {{
            font-weight: 600;
            color: #1a1c1b;
            font-size: 15px;
        }}
        button {{
            width: 100%;
            padding: 16px;
            background: #c24e2c;
            color: white;
            border: none;
            border-radius: 50px;
            font-size: 16px;
            font-weight: 700;
            font-family: 'Plus Jakarta Sans', sans-serif;
            cursor: pointer;
            transition: all 0.2s;
            margin-top: 12px;
        }}
        button:hover {{
            box-shadow: 0 8px 20px rgba(194, 78, 44, 0.3);
            transform: scale(1.02);
        }}
        .no-boards {{
            color: #645d56;
            text-align: center;
            padding: 32px 20px;
            background: #f4f3f1;
            border-radius: 16px;
        }}
        .no-boards p {{ margin-bottom: 8px; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
            </svg>
        </div>
        <span class="brand">Boardy</span>
    </div>
    <div class="card">
        <h2>Authorize access</h2>
        <p class="scope"><strong>{client_name}</strong> is requesting <code>{scope}</code></p>
        <form method="POST">
            <input type="hidden" name="client_id" value="{client_id}">
            <input type="hidden" name="redirect_uri" value="{redirect_uri}">
            <input type="hidden" name="response_type" value="{response_type}">
            <input type="hidden" name="state" value="{state}">
            <input type="hidden" name="scope" value="{scope}">
            <input type="hidden" name="code_challenge" value="{code_challenge}">
            <input type="hidden" name="code_challenge_method" value="{code_challenge_method}">
            <input type="hidden" name="user_id" value="{user_id}">

            <h3>Select a board to share:</h3>
            {boards_html}

            <button type="submit">Allow access</button>
        </form>
    </div>
</body>
</html>"""


# ─── Helper Functions ───────────────────────────────────────────────────

def verify_pkce(code_verifier: str, code_challenge: str) -> bool:
    """Verify PKCE S256 challenge."""
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    computed = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return computed == code_challenge


def oauth_error_response(
    error: str,
    description: str,
    status_code: int = 400
) -> JSONResponse:
    """Return an OAuth 2.1 compliant error response."""
    return JSONResponse(
        status_code=status_code,
        content={"error": error, "error_description": description}
    )


def oauth_error_redirect(
    redirect_uri: str,
    error: str,
    description: str,
    state: Optional[str] = None
) -> RedirectResponse:
    """Redirect with OAuth error params."""
    params = f"error={error}&error_description={description}"
    if state:
        params += f"&state={state}"
    return RedirectResponse(f"{redirect_uri}?{params}", status_code=302)


# ─── Discovery Endpoint ─────────────────────────────────────────────────

@discovery_router.get("/.well-known/oauth-authorization-server")
def oauth_metadata():
    """RFC 8414 OAuth Authorization Server Metadata."""
    base_url = settings.app_url
    return {
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/auth/authorize",
        "token_endpoint": f"{base_url}/auth/token",
        "registration_endpoint": f"{base_url}/auth/register",
        "scopes_supported": ["board:read", "board:write"],
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "code_challenge_methods_supported": ["S256"],
        "token_endpoint_auth_methods_supported": ["client_secret_post", "client_secret_basic"],
    }


# ─── Client Registration (RFC 7591) ─────────────────────────────────────

@oauth_router.post("/register", response_model=ClientRegistrationResponse)
def register_client(
    request: ClientRegistrationRequest,
    session: Session = Depends(get_session)
):
    """Dynamic Client Registration (RFC 7591)."""
    if not request.redirect_uris:
        raise HTTPException(400, "redirect_uris is required")

    # Validate redirect URIs (must be HTTPS, except localhost)
    for uri in request.redirect_uris:
        if not uri.startswith("https://") and "localhost" not in uri:
            raise HTTPException(400, f"Invalid redirect_uri: {uri} (must be HTTPS)")

    client_id = secrets.token_urlsafe(16)
    client_secret = secrets.token_urlsafe(32)

    client = OAuthClient(
        client_id=client_id,
        client_secret=client_secret,
        client_name=request.client_name,
        redirect_uris=json.dumps(request.redirect_uris),
        scope="board:read board:write",
    )
    session.add(client)
    session.commit()
    session.refresh(client)

    logger.info(f"Registered OAuth client: {client.client_name} ({client.client_id})")

    return ClientRegistrationResponse(
        client_id=client.client_id,
        client_secret=client.client_secret,
        client_name=client.client_name,
        redirect_uris=request.redirect_uris,
        scope=client.scope,
    )


# ─── Authorization Endpoint ─────────────────────────────────────────────

@oauth_router.get("/authorize", response_class=HTMLResponse)
def authorize_get(
    client_id: str = Query(...),
    redirect_uri: str = Query(...),
    response_type: str = Query(...),
    state: str = Query(...),
    code_challenge: str = Query(...),
    code_challenge_method: str = Query(...),
    scope: str = Query("board:read board:write"),
    session: Session = Depends(get_session),
):
    """Display authorization page (login or board selection)."""
    # Validate response_type
    if response_type != "code":
        return oauth_error_redirect(
            redirect_uri, "unsupported_response_type",
            "Only 'code' response type is supported", state
        )

    # Validate PKCE method
    if code_challenge_method != "S256":
        return oauth_error_redirect(
            redirect_uri, "invalid_request",
            "Only S256 code_challenge_method is supported", state
        )

    # Validate client
    client = session.exec(
        select(OAuthClient).where(OAuthClient.client_id == client_id)
    ).first()
    if not client:
        return oauth_error_redirect(
            redirect_uri, "invalid_client",
            "Unknown client_id", state
        )

    # Validate redirect_uri
    registered_uris = json.loads(client.redirect_uris)
    if redirect_uri not in registered_uris:
        return oauth_error_redirect(
            redirect_uri, "invalid_request",
            "redirect_uri not registered for this client", state
        )

    # Show login form (user not authenticated yet in this flow)
    return HTMLResponse(LOGIN_PAGE_TEMPLATE.format(
        client_id=client_id,
        client_name=client.client_name,
        redirect_uri=redirect_uri,
        response_type=response_type,
        state=state,
        scope=scope,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
        error_html="",
    ))


@oauth_router.post("/authorize")
def authorize_post(
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    response_type: str = Form(...),
    state: str = Form(...),
    code_challenge: str = Form(...),
    code_challenge_method: str = Form(...),
    scope: str = Form("board:read board:write"),
    email: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    board_id: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),
    session: Session = Depends(get_session),
):
    """Process authorization (login or board selection)."""
    # Get client
    client = session.exec(
        select(OAuthClient).where(OAuthClient.client_id == client_id)
    ).first()
    if not client:
        return oauth_error_redirect(
            redirect_uri, "invalid_client", "Unknown client_id", state
        )

    # Case 1: User submitted login form
    if email and password:
        user = authenticate_user(session, email, password)
        if not user:
            return HTMLResponse(LOGIN_PAGE_TEMPLATE.format(
                client_id=client_id,
                client_name=client.client_name,
                redirect_uri=redirect_uri,
                response_type=response_type,
                state=state,
                scope=scope,
                code_challenge=code_challenge,
                code_challenge_method=code_challenge_method,
                error_html='<div class="error">Invalid email or password</div>',
            ))

        # User authenticated, show board selection
        boards = get_boards(session, user.id)
        if not boards:
            boards_html = '<p class="no-boards">You have no boards. Create one first.</p>'
        else:
            boards_html = ""
            for i, board in enumerate(boards):
                checked = "checked" if i == 0 else ""
                boards_html += f'''
                <label class="board-option">
                    <input type="radio" name="board_id" value="{board.id}" {checked}>
                    <span class="board-name">{board.name}</span>
                </label>
                '''

        return HTMLResponse(BOARD_SELECTION_TEMPLATE.format(
            client_id=client_id,
            client_name=client.client_name,
            redirect_uri=redirect_uri,
            response_type=response_type,
            state=state,
            scope=scope,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            user_id=user.id,
            boards_html=boards_html,
        ))

    # Case 2: User selected a board
    if user_id and board_id:
        # Verify user owns the board
        board = get_board(session, board_id, user_id)
        if not board:
            return oauth_error_redirect(
                redirect_uri, "access_denied",
                "Board not found or not accessible", state
            )

        # Generate authorization code
        code = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=settings.oauth_auth_code_expire_seconds
        )

        auth_code = OAuthAuthCode(
            code=code,
            client_id=client_id,
            user_id=user_id,
            board_id=board_id,
            scope=scope,
            redirect_uri=redirect_uri,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            expires_at=expires_at,
        )
        session.add(auth_code)
        session.commit()

        logger.info(f"Issued auth code for user {user_id}, board {board_id}")

        # Redirect with code
        return RedirectResponse(
            f"{redirect_uri}?code={code}&state={state}",
            status_code=302
        )

    # Invalid request
    return oauth_error_redirect(
        redirect_uri, "invalid_request",
        "Missing required parameters", state
    )


# ─── Token Endpoint ─────────────────────────────────────────────────────

@oauth_router.post("/token")
def token(
    grant_type: str = Form(...),
    code: Optional[str] = Form(None),
    redirect_uri: Optional[str] = Form(None),
    client_id: str = Form(...),
    client_secret: str = Form(...),
    code_verifier: Optional[str] = Form(None),
    refresh_token: Optional[str] = Form(None),
    session: Session = Depends(get_session),
):
    """Exchange authorization code for tokens."""
    # Validate client credentials
    client = session.exec(
        select(OAuthClient).where(
            OAuthClient.client_id == client_id,
            OAuthClient.client_secret == client_secret
        )
    ).first()
    if not client:
        return oauth_error_response("invalid_client", "Invalid client credentials", 401)

    # Handle authorization_code grant
    if grant_type == "authorization_code":
        if not code or not code_verifier or not redirect_uri:
            return oauth_error_response(
                "invalid_request",
                "Missing code, code_verifier, or redirect_uri"
            )

        # Look up auth code
        auth_code = session.exec(
            select(OAuthAuthCode).where(OAuthAuthCode.code == code)
        ).first()

        if not auth_code:
            return oauth_error_response("invalid_grant", "Invalid authorization code")

        if auth_code.used:
            return oauth_error_response("invalid_grant", "Authorization code already used")

        # Handle both naive and aware datetimes from DB
        expires_at = auth_code.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            return oauth_error_response("invalid_grant", "Authorization code expired")

        if auth_code.client_id != client_id:
            return oauth_error_response("invalid_grant", "Code was not issued to this client")

        if auth_code.redirect_uri != redirect_uri:
            return oauth_error_response("invalid_grant", "redirect_uri mismatch")

        # Verify PKCE
        if not verify_pkce(code_verifier, auth_code.code_challenge):
            return oauth_error_response("invalid_grant", "Invalid code_verifier")

        # Mark code as used
        auth_code.used = True
        session.add(auth_code)

        # Generate tokens
        access_token = secrets.token_urlsafe(32)
        new_refresh_token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=settings.oauth_access_token_expire_seconds
        )

        oauth_token = OAuthToken(
            client_id=client_id,
            user_id=auth_code.user_id,
            board_id=auth_code.board_id,
            access_token=access_token,
            refresh_token=new_refresh_token,
            scope=auth_code.scope,
            expires_at=expires_at,
        )
        session.add(oauth_token)
        session.commit()

        logger.info(f"Issued access token for user {auth_code.user_id}, board {auth_code.board_id}")

        return TokenResponse(
            access_token=access_token,
            expires_in=settings.oauth_access_token_expire_seconds,
            refresh_token=new_refresh_token,
            scope=auth_code.scope,
        )

    # Handle refresh_token grant
    elif grant_type == "refresh_token":
        if not refresh_token:
            return oauth_error_response("invalid_request", "Missing refresh_token")

        # Look up existing token
        existing = session.exec(
            select(OAuthToken).where(
                OAuthToken.refresh_token == refresh_token,
                OAuthToken.client_id == client_id
            )
        ).first()

        if not existing:
            return oauth_error_response("invalid_grant", "Invalid refresh token")

        # Generate new tokens (rotate refresh token)
        new_access_token = secrets.token_urlsafe(32)
        new_refresh_token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=settings.oauth_access_token_expire_seconds
        )

        # Update existing token record
        existing.access_token = new_access_token
        existing.refresh_token = new_refresh_token
        existing.expires_at = expires_at
        session.add(existing)
        session.commit()

        logger.info(f"Refreshed access token for user {existing.user_id}")

        return TokenResponse(
            access_token=new_access_token,
            expires_in=settings.oauth_access_token_expire_seconds,
            refresh_token=new_refresh_token,
            scope=existing.scope,
        )

    else:
        return oauth_error_response(
            "unsupported_grant_type",
            f"Grant type '{grant_type}' not supported"
        )
