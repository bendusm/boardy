"""OAuth 2.1 Authorization Server for Boardy MCP integration."""

from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import urlencode, urlparse
import secrets
import hashlib
import hmac
import base64
import html
import json
import logging
import time

from fastapi import APIRouter, Depends, Form, Query, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from app.core.rate_limit import token_rate_limiter, auth_code_rate_limiter
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.config import settings
from .models import OAuthClient, OAuthAuthCode, OAuthToken, User
from .service import authenticate_user
from app.boards.service import get_boards, get_board, get_board_with_access

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


# ─── CSRF Session Token ────────────────────────────────────────────────

SESSION_TOKEN_MAX_AGE = 600  # 10 minutes


def create_session_token(user_id: str) -> str:
    """Create a signed session token binding user_id to the OAuth flow.

    Token format: base64(user_id:timestamp:signature)
    Security: Uses full HMAC-SHA256 output (256 bits) for collision resistance.
    """
    timestamp = str(int(time.time()))
    payload = f"{user_id}:{timestamp}"
    # Security: Use full HMAC output (64 hex chars = 256 bits)
    signature = hmac.new(
        settings.secret_key.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    token = f"{payload}:{signature}"
    return base64.urlsafe_b64encode(token.encode()).decode()


def verify_session_token(token: str, expected_user_id: str) -> bool:
    """Verify session token is valid and matches expected user_id.

    Security: Uses constant-time comparison to prevent timing attacks.
    """
    try:
        decoded = base64.urlsafe_b64decode(token.encode()).decode()
        parts = decoded.split(":", 2)  # Split into max 3 parts (user_id:timestamp:signature)
        if len(parts) != 3:
            return False

        user_id, timestamp, signature = parts

        # Verify user_id matches
        if user_id != expected_user_id:
            return False

        # Verify not expired
        token_time = int(timestamp)
        if time.time() - token_time > SESSION_TOKEN_MAX_AGE:
            return False

        # Security: Use full HMAC output and constant-time comparison
        payload = f"{user_id}:{timestamp}"
        expected_sig = hmac.new(
            settings.secret_key.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_sig)
    except Exception:
        return False


# ─── HTML Templates ─────────────────────────────────────────────────────

LOGIN_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Boardy - Sign In</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        @font-face {{
            font-family: 'Plus Jakarta Sans';
            font-style: normal;
            font-weight: 400;
            font-display: swap;
            src: url('/fonts/PlusJakartaSans-Regular.woff2') format('woff2');
        }}
        @font-face {{
            font-family: 'Plus Jakarta Sans';
            font-style: normal;
            font-weight: 600;
            font-display: swap;
            src: url('/fonts/PlusJakartaSans-SemiBold.woff2') format('woff2');
        }}
        @font-face {{
            font-family: 'Newsreader';
            font-style: italic;
            font-weight: 700;
            font-display: swap;
            src: url('/fonts/Newsreader-BoldItalic.woff2') format('woff2');
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
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
    <style>
        @font-face {{
            font-family: 'Plus Jakarta Sans';
            font-style: normal;
            font-weight: 400;
            font-display: swap;
            src: url('/fonts/PlusJakartaSans-Regular.woff2') format('woff2');
        }}
        @font-face {{
            font-family: 'Plus Jakarta Sans';
            font-style: normal;
            font-weight: 600;
            font-display: swap;
            src: url('/fonts/PlusJakartaSans-SemiBold.woff2') format('woff2');
        }}
        @font-face {{
            font-family: 'Newsreader';
            font-style: italic;
            font-weight: 700;
            font-display: swap;
            src: url('/fonts/Newsreader-BoldItalic.woff2') format('woff2');
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
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
            <input type="hidden" name="session_token" value="{session_token}">

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
    """Redirect with OAuth error params.

    Security: All parameters are URL-encoded to prevent parameter injection attacks.
    """
    params = {"error": error, "error_description": description}
    if state:
        params["state"] = state
    return RedirectResponse(f"{redirect_uri}?{urlencode(params)}", status_code=302)


def validate_scope(requested_scope: str, client_scope: str) -> bool:
    """Validate that requested scopes are a subset of client's registered scopes.

    Security: Prevents scope escalation attacks where clients request more permissions
    than they were registered with.
    """
    requested = set(requested_scope.split())
    allowed = set(client_scope.split())
    return requested.issubset(allowed)


# Allowed redirect URI patterns for OAuth callbacks
# Security: Restricts OAuth callbacks to trusted domains only
# Format: (scheme, hostname, port or None for default)
ALLOWED_REDIRECT_ORIGINS = [
    ("https", "claude.ai", None),
    ("http", "localhost", None),  # Any port on localhost
    ("http", "127.0.0.1", None),  # Any port on 127.0.0.1
]


def is_allowed_redirect_uri(uri: str) -> bool:
    """Check if redirect URI is from an allowed origin.

    Security: Prevents OAuth token interception via malicious redirect URIs.
    Uses proper URL parsing to prevent bypasses like:
    - https://claude.ai.attacker.com (subdomain attack)
    - http://localhost@attacker.com (userinfo attack)
    """
    try:
        parsed = urlparse(uri)
    except Exception:
        return False

    # Reject URLs with userinfo (user:pass@host attack vector)
    if parsed.username or parsed.password:
        return False

    # Must have scheme and hostname
    if not parsed.scheme or not parsed.hostname:
        return False

    for allowed_scheme, allowed_host, allowed_port in ALLOWED_REDIRECT_ORIGINS:
        if parsed.scheme != allowed_scheme:
            continue
        if parsed.hostname != allowed_host:
            continue
        # If allowed_port is None, accept any port; otherwise must match exactly
        if allowed_port is not None and parsed.port != allowed_port:
            continue
        return True

    return False


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
        "revocation_endpoint": f"{base_url}/auth/revoke",
        "scopes_supported": ["board:read", "board:write"],
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "code_challenge_methods_supported": ["S256"],
        "token_endpoint_auth_methods_supported": ["client_secret_post", "client_secret_basic"],
        "revocation_endpoint_auth_methods_supported": ["client_secret_post"],
    }


@discovery_router.get("/.well-known/oauth-protected-resource")
def protected_resource_metadata():
    """RFC 9728 OAuth 2.0 Protected Resource Metadata.

    This endpoint tells MCP clients how to authenticate with the Boardy MCP server.
    Required for Anthropic MCP Directory listing.
    """
    base_url = settings.app_url
    return {
        "resource": f"{base_url}/mcp",
        "authorization_servers": [base_url],
        "scopes_supported": ["board:read", "board:write"],
        "bearer_methods_supported": ["header"],
        "resource_documentation": f"{base_url}/docs",
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

    # Security: Validate redirect URIs against whitelist
    for uri in request.redirect_uris:
        if not is_allowed_redirect_uri(uri):
            raise HTTPException(
                400,
                f"Invalid redirect_uri: {uri}. Only claude.ai and localhost are allowed."
            )

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
    request: Request,
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
    # Security: Rate limit authorization attempts
    auth_code_rate_limiter.check(request)

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
        # Security: Don't redirect to unregistered URI - return error response instead
        return oauth_error_response(
            "invalid_request",
            "redirect_uri not registered for this client",
            400
        )

    # Security: Validate requested scope against client's registered scope
    if not validate_scope(scope, client.scope):
        return oauth_error_redirect(
            redirect_uri, "invalid_scope",
            "Requested scope exceeds client registration", state
        )

    # Show login form (user not authenticated yet in this flow)
    return HTMLResponse(LOGIN_PAGE_TEMPLATE.format(
        client_id=client_id,
        client_name=html.escape(client.client_name),
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
    request: Request,
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
    session_token: Optional[str] = Form(None),
    session: Session = Depends(get_session),
):
    """Process authorization (login or board selection)."""
    # Security: Rate limit authorization attempts (includes login form submissions)
    auth_code_rate_limiter.check(request)

    # Get client
    client = session.exec(
        select(OAuthClient).where(OAuthClient.client_id == client_id)
    ).first()
    if not client:
        # Security: Don't redirect to potentially malicious URI
        return oauth_error_response("invalid_client", "Unknown client_id", 400)

    # Validate redirect_uri is registered
    registered_uris = json.loads(client.redirect_uris)
    if redirect_uri not in registered_uris:
        return oauth_error_response(
            "invalid_request",
            "redirect_uri not registered for this client",
            400
        )

    # Security: Validate requested scope
    if not validate_scope(scope, client.scope):
        return oauth_error_redirect(
            redirect_uri, "invalid_scope",
            "Requested scope exceeds client registration", state
        )

    # Case 1: User submitted login form
    if email and password:
        user = authenticate_user(session, email, password)
        if not user:
            return HTMLResponse(LOGIN_PAGE_TEMPLATE.format(
                client_id=client_id,
                client_name=html.escape(client.client_name),
                redirect_uri=redirect_uri,
                response_type=response_type,
                state=state,
                scope=scope,
                code_challenge=code_challenge,
                code_challenge_method=code_challenge_method,
                error_html='<div class="error">Invalid email or password</div>',
            ))

        # User authenticated, show board selection
        boards_with_roles = get_boards(session, user.id)
        if not boards_with_roles:
            boards_html = '<p class="no-boards">You have no boards. Create one first.</p>'
        else:
            boards_html = ""
            for i, (board, role) in enumerate(boards_with_roles):
                checked = "checked" if i == 0 else ""
                boards_html += f'''
                <label class="board-option">
                    <input type="radio" name="board_id" value="{html.escape(board.id)}" {checked}>
                    <span class="board-name">{html.escape(board.name)}</span>
                </label>
                '''

        # Generate signed session token to prevent CSRF/tampering
        session_token = create_session_token(user.id)

        return HTMLResponse(BOARD_SELECTION_TEMPLATE.format(
            client_id=client_id,
            client_name=html.escape(client.client_name),
            redirect_uri=redirect_uri,
            response_type=response_type,
            state=state,
            scope=scope,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            user_id=user.id,
            session_token=session_token,
            boards_html=boards_html,
        ))

    # Case 2: User selected a board
    if user_id and board_id:
        # Security: Verify session token to prevent CSRF/user_id tampering
        if not session_token or not verify_session_token(session_token, user_id):
            return oauth_error_redirect(
                redirect_uri, "access_denied",
                "Invalid or expired session. Please try again.", state
            )

        # Verify user has access to the board (owner or member)
        board_result = get_board_with_access(session, board_id, user_id)
        if not board_result:
            return oauth_error_redirect(
                redirect_uri, "access_denied",
                "Board not found or not accessible", state
            )
        board, user_role = board_result

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
    request: Request,
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
    # Security: Rate limit by IP + client_id
    token_rate_limiter.check(request, key_suffix=client_id)

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

        # Security: Re-verify user still has board access before issuing token
        board_result = get_board_with_access(session, auth_code.board_id, auth_code.user_id)
        if not board_result:
            return oauth_error_response("invalid_grant", "Board no longer accessible")
        board, _ = board_result

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


# ─── Token Revocation (RFC 7009) ────────────────────────────────────────

@oauth_router.post("/revoke")
def revoke_token(
    token: str = Form(...),
    token_type_hint: Optional[str] = Form(None),
    client_id: str = Form(...),
    client_secret: str = Form(...),
    session: Session = Depends(get_session)
):
    """Revoke an access or refresh token (RFC 7009).

    Security: Allows users/clients to invalidate tokens that may be compromised.
    """
    # Authenticate client
    client = session.exec(
        select(OAuthClient).where(OAuthClient.client_id == client_id)
    ).first()

    if not client or client.client_secret != client_secret:
        # RFC 7009: Return 200 even on invalid client to prevent enumeration
        logger.warning(f"Token revocation: invalid client {client_id}")
        return JSONResponse(content={}, status_code=200)

    # Try to find and delete the token
    # Check access_token first, then refresh_token
    oauth_token = None

    if token_type_hint == "refresh_token":
        # Hint says it's a refresh token - check that first
        oauth_token = session.exec(
            select(OAuthToken).where(OAuthToken.refresh_token == token)
        ).first()
        if not oauth_token:
            oauth_token = session.exec(
                select(OAuthToken).where(OAuthToken.access_token == token)
            ).first()
    else:
        # Default: check access_token first
        oauth_token = session.exec(
            select(OAuthToken).where(OAuthToken.access_token == token)
        ).first()
        if not oauth_token:
            oauth_token = session.exec(
                select(OAuthToken).where(OAuthToken.refresh_token == token)
            ).first()

    if oauth_token:
        # Verify the token belongs to this client
        if oauth_token.client_id == client_id:
            session.delete(oauth_token)
            session.commit()
            logger.info(f"Revoked token for user {oauth_token.user_id}, client {client_id}")
        else:
            logger.warning(f"Token revocation: client mismatch for token")

    # RFC 7009: Always return 200, even if token wasn't found (prevents enumeration)
    return JSONResponse(content={}, status_code=200)
