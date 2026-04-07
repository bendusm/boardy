from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from sqlmodel import Session, text

from app.core.config import settings
from app.core.security_headers import SecurityHeadersMiddleware
from app.core.database import get_session
from app.core.database import create_db_and_tables
from app.auth.router import router as auth_router
from app.auth.oauth_router import discovery_router, oauth_router
from app.boards.router import router as boards_router
from app.boards.members_router import router as members_router
from app.mcp_server import mcp

# Get MCP HTTP app for mounting
mcp_app = mcp.http_app()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    # Initialize FastMCP lifespan
    async with mcp_app.lifespan(app):
        yield


app = FastAPI(
    title="Boardy API",
    description="Claude-powered Kanban SaaS",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", settings.app_url],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With", "X-CSRF-Token"],
)

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(boards_router, prefix="/api/v1", tags=["boards"])
app.include_router(members_router, prefix="/api/v1", tags=["members"])

# OAuth 2.1 endpoints (both /auth/* for web UI and /* for MCP)
app.include_router(discovery_router)  # /.well-known/oauth-authorization-server
app.include_router(oauth_router, prefix="/auth", tags=["oauth"])
app.include_router(oauth_router, tags=["oauth-mcp"])  # /authorize, /token for MCP

# MCP server
app.mount("/mcp", mcp_app)


@app.get("/health")
def health(session: Session = Depends(get_session)):
    """Health check endpoint with database connectivity verification."""
    try:
        session.exec(text("SELECT 1"))
        return {"status": "ok", "app": settings.app_name, "database": "connected"}
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "degraded", "app": settings.app_name, "database": "disconnected"}
        )
