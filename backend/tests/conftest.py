"""Pytest fixtures for Boardy backend tests.

Requirements:
    - PostgreSQL must be running (docker compose up -d postgres)
    - Uses the same database as development (boardy)
"""

import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone

import pytest
from sqlmodel import Session, SQLModel

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_session, engine
from app.auth.models import User, OAuthClient, OAuthAuthCode, OAuthToken
from app.boards.models import Board, BoardMember, Column, Card, BoardRole, CreatedBy


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all tables once per test session."""
    SQLModel.metadata.create_all(engine)
    yield


@pytest.fixture(name="session")
def session_fixture():
    """Create database session for testing with transaction rollback."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    # Rollback to clean up test data
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(name="client")
def client_fixture(session):
    """Create test client with database session override."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session):
    """Create a test user."""
    from passlib.hash import bcrypt

    user = User(
        id="01HX1234567890ABCDEFGHIJ",
        email="test@example.com",
        password_hash=bcrypt.hash("testpassword123"),
        terms_accepted_at=datetime.now(timezone.utc),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="test_board")
def test_board_fixture(session, test_user):
    """Create a test board with columns."""
    board = Board(
        id="01HX9876543210ZYXWVUTSRQ",
        name="Test Board",
        slug="test-board",
        owner_id=test_user.id,
    )
    session.add(board)
    session.commit()

    # Add user as owner
    member = BoardMember(
        board_id=board.id,
        user_id=test_user.id,
        role=BoardRole.owner,
    )
    session.add(member)

    # Create default columns
    columns = [
        Column(id="01HXCOL1000000000000001", board_id=board.id, name="To Do", position=0),
        Column(id="01HXCOL2000000000000002", board_id=board.id, name="In Progress", position=1),
        Column(id="01HXCOL3000000000000003", board_id=board.id, name="Done", position=2),
    ]
    for col in columns:
        session.add(col)

    session.commit()
    session.refresh(board)
    return board


@pytest.fixture(name="test_card")
def test_card_fixture(session, test_board):
    """Create a test card."""
    card = Card(
        id="01HXCARD00000000000001",
        board_id=test_board.id,
        column_id="01HXCOL1000000000000001",
        title="Test Card",
        description="Test description",
        position=0,
        created_by=CreatedBy.user,
    )
    session.add(card)
    session.commit()
    session.refresh(card)
    return card


@pytest.fixture(name="oauth_client")
def oauth_client_fixture(session):
    """Create a test OAuth client."""
    import json

    client = OAuthClient(
        client_id="test_client_id",
        client_secret="test_client_secret",
        client_name="Test MCP Client",
        redirect_uris=json.dumps(["https://claude.ai/api/mcp/auth_callback"]),
        scope="board:read board:write",
    )
    session.add(client)
    session.commit()
    session.refresh(client)
    return client


@pytest.fixture(name="oauth_auth_code")
def oauth_auth_code_fixture(session, oauth_client, test_user, test_board):
    """Create a test OAuth authorization code."""
    # Generate PKCE values
    code_verifier = secrets.token_urlsafe(32)
    code_challenge = hashlib.sha256(code_verifier.encode()).digest()
    import base64
    code_challenge_b64 = base64.urlsafe_b64encode(code_challenge).rstrip(b"=").decode()

    auth_code = OAuthAuthCode(
        code=secrets.token_urlsafe(32),
        client_id=oauth_client.client_id,
        user_id=test_user.id,
        board_id=test_board.id,
        scope="board:read board:write",
        code_challenge=code_challenge_b64,
        code_challenge_method="S256",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        used=False,
    )
    session.add(auth_code)
    session.commit()
    session.refresh(auth_code)

    # Return both code and verifier
    return {"code": auth_code, "verifier": code_verifier}


@pytest.fixture(name="oauth_token")
def oauth_token_fixture(session, oauth_client, test_user, test_board):
    """Create a test OAuth access token."""
    token = OAuthToken(
        client_id=oauth_client.client_id,
        user_id=test_user.id,
        board_id=test_board.id,
        access_token="test_access_token_" + secrets.token_urlsafe(16),
        refresh_token="test_refresh_token_" + secrets.token_urlsafe(16),
        scope="board:read board:write",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    session.add(token)
    session.commit()
    session.refresh(token)
    return token
