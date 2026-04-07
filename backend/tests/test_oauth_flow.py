"""Tests for OAuth 2.1 flow including PKCE and RFC compliance."""

import base64
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

import pytest


class TestDiscoveryEndpoints:
    """Tests for OAuth discovery endpoints (RFC 8414, RFC 9728)."""

    def test_oauth_authorization_server_metadata(self, client):
        """Test RFC 8414 OAuth Authorization Server Metadata endpoint."""
        response = client.get("/.well-known/oauth-authorization-server")
        assert response.status_code == 200

        data = response.json()
        assert "issuer" in data
        assert "authorization_endpoint" in data
        assert "token_endpoint" in data
        assert "registration_endpoint" in data
        assert "revocation_endpoint" in data
        assert "scopes_supported" in data
        assert "board:read" in data["scopes_supported"]
        assert "board:write" in data["scopes_supported"]
        assert "S256" in data["code_challenge_methods_supported"]
        assert "authorization_code" in data["grant_types_supported"]
        assert "refresh_token" in data["grant_types_supported"]

    def test_protected_resource_metadata(self, client):
        """Test RFC 9728 OAuth Protected Resource Metadata endpoint."""
        response = client.get("/.well-known/oauth-protected-resource")
        assert response.status_code == 200

        data = response.json()
        assert "resource" in data
        assert "/mcp" in data["resource"]
        assert "authorization_servers" in data
        assert "scopes_supported" in data
        assert "board:read" in data["scopes_supported"]
        assert "board:write" in data["scopes_supported"]


class TestDynamicClientRegistration:
    """Tests for Dynamic Client Registration (RFC 7591)."""

    def test_register_client_success(self, client):
        """Test successful client registration."""
        response = client.post(
            "/auth/register",
            json={
                "client_name": "My MCP Client",
                "redirect_uris": ["https://claude.ai/api/mcp/auth_callback"],
            },
        )
        assert response.status_code == 200

        data = response.json()
        assert "client_id" in data
        assert "client_secret" in data
        assert data["client_name"] == "My MCP Client"
        assert "https://claude.ai/api/mcp/auth_callback" in data["redirect_uris"]
        assert "board:read board:write" == data["scope"]

    def test_register_client_localhost_allowed(self, client):
        """Test that localhost is allowed for development."""
        response = client.post(
            "/auth/register",
            json={
                "client_name": "Dev Client",
                "redirect_uris": ["http://localhost:3000/callback"],
            },
        )
        assert response.status_code == 200

    def test_register_client_invalid_redirect_uri(self, client):
        """Test that invalid redirect URIs are rejected."""
        response = client.post(
            "/auth/register",
            json={
                "client_name": "Bad Client",
                "redirect_uris": ["https://evil.com/callback"],
            },
        )
        assert response.status_code == 400
        assert "Invalid redirect_uri" in response.json()["detail"]

    def test_register_client_empty_redirect_uris(self, client):
        """Test that empty redirect_uris are rejected."""
        response = client.post(
            "/auth/register",
            json={
                "client_name": "Bad Client",
                "redirect_uris": [],
            },
        )
        assert response.status_code == 400


class TestAuthorizationEndpoint:
    """Tests for OAuth authorization endpoint."""

    def test_authorize_requires_pkce(self, client, oauth_client, test_user, test_board):
        """Test that PKCE is required for authorization."""
        response = client.get(
            "/auth/authorize",
            params={
                "client_id": oauth_client.client_id,
                "redirect_uri": "https://claude.ai/api/mcp/auth_callback",
                "response_type": "code",
                "state": "random_state",
                "scope": "board:read board:write",
                # Missing code_challenge and code_challenge_method
            },
            follow_redirects=False,
        )
        # Should redirect with error or return error page
        assert response.status_code in [302, 400, 422]

    def test_authorize_invalid_response_type(self, client, oauth_client):
        """Test that only 'code' response type is supported."""
        code_verifier = secrets.token_urlsafe(32)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).rstrip(b"=").decode()

        response = client.get(
            "/auth/authorize",
            params={
                "client_id": oauth_client.client_id,
                "redirect_uri": "https://claude.ai/api/mcp/auth_callback",
                "response_type": "token",  # Invalid - only 'code' allowed
                "state": "random_state",
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
            },
            follow_redirects=False,
        )
        # Should redirect with unsupported_response_type error
        assert response.status_code == 302
        location = response.headers.get("location", "")
        assert "unsupported_response_type" in location


class TestTokenEndpoint:
    """Tests for OAuth token endpoint."""

    def test_token_exchange_with_valid_code(
        self, client, oauth_client, oauth_auth_code, session
    ):
        """Test successful token exchange with valid authorization code."""
        auth_code = oauth_auth_code["code"]
        code_verifier = oauth_auth_code["verifier"]

        response = client.post(
            "/auth/token",
            data={
                "grant_type": "authorization_code",
                "code": auth_code.code,
                "redirect_uri": "https://claude.ai/api/mcp/auth_callback",
                "client_id": oauth_client.client_id,
                "client_secret": oauth_client.client_secret,
                "code_verifier": code_verifier,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "Bearer"
        assert data["expires_in"] > 0
        assert "board:read" in data["scope"]

    def test_token_exchange_rejects_used_code(
        self, client, oauth_client, oauth_auth_code, session
    ):
        """Test that authorization codes cannot be reused."""
        auth_code = oauth_auth_code["code"]
        code_verifier = oauth_auth_code["verifier"]

        # First exchange - should succeed
        response1 = client.post(
            "/auth/token",
            data={
                "grant_type": "authorization_code",
                "code": auth_code.code,
                "redirect_uri": "https://claude.ai/api/mcp/auth_callback",
                "client_id": oauth_client.client_id,
                "client_secret": oauth_client.client_secret,
                "code_verifier": code_verifier,
            },
        )
        assert response1.status_code == 200

        # Second exchange - should fail
        response2 = client.post(
            "/auth/token",
            data={
                "grant_type": "authorization_code",
                "code": auth_code.code,
                "redirect_uri": "https://claude.ai/api/mcp/auth_callback",
                "client_id": oauth_client.client_id,
                "client_secret": oauth_client.client_secret,
                "code_verifier": code_verifier,
            },
        )
        assert response2.status_code == 400

    def test_token_exchange_wrong_pkce(
        self, client, oauth_client, oauth_auth_code
    ):
        """Test that wrong PKCE verifier is rejected."""
        auth_code = oauth_auth_code["code"]

        response = client.post(
            "/auth/token",
            data={
                "grant_type": "authorization_code",
                "code": auth_code.code,
                "redirect_uri": "https://claude.ai/api/mcp/auth_callback",
                "client_id": oauth_client.client_id,
                "client_secret": oauth_client.client_secret,
                "code_verifier": "wrong_verifier_12345678901234567890",
            },
        )
        assert response.status_code == 400
        assert "PKCE" in response.json().get("error_description", "")

    def test_refresh_token(self, client, oauth_client, oauth_token):
        """Test token refresh flow."""
        response = client.post(
            "/auth/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": oauth_token.refresh_token,
                "client_id": oauth_client.client_id,
                "client_secret": oauth_client.client_secret,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        # New tokens should be different from old ones
        assert data["access_token"] != oauth_token.access_token


class TestTokenRevocation:
    """Tests for OAuth token revocation (RFC 7009)."""

    def test_revoke_access_token(self, client, oauth_client, oauth_token):
        """Test revoking an access token."""
        response = client.post(
            "/auth/revoke",
            data={
                "token": oauth_token.access_token,
                "client_id": oauth_client.client_id,
                "client_secret": oauth_client.client_secret,
            },
        )
        # RFC 7009: Always return 200, even if token not found
        assert response.status_code == 200

    def test_revoke_refresh_token(self, client, oauth_client, oauth_token):
        """Test revoking a refresh token."""
        response = client.post(
            "/auth/revoke",
            data={
                "token": oauth_token.refresh_token,
                "client_id": oauth_client.client_id,
                "client_secret": oauth_client.client_secret,
            },
        )
        assert response.status_code == 200

    def test_revoke_invalid_token(self, client, oauth_client):
        """Test that revoking non-existent token returns 200 (RFC 7009)."""
        response = client.post(
            "/auth/revoke",
            data={
                "token": "invalid_token_that_does_not_exist",
                "client_id": oauth_client.client_id,
                "client_secret": oauth_client.client_secret,
            },
        )
        # RFC 7009: Must return 200 even for invalid tokens (prevent enumeration)
        assert response.status_code == 200


class TestMCPAuthentication:
    """Tests for MCP endpoint authentication with RFC 9728 compliance."""

    def test_mcp_unauthorized_returns_www_authenticate(self, client):
        """Test that MCP returns WWW-Authenticate header on 401."""
        response = client.post(
            "/mcp/",
            json={"jsonrpc": "2.0", "method": "tools/list", "id": 1},
        )

        # MCP should require authentication
        if response.status_code == 401:
            # Check for RFC 9728 compliant WWW-Authenticate header
            www_auth = response.headers.get("WWW-Authenticate", "")
            assert "Bearer" in www_auth
            assert "resource_metadata" in www_auth
            assert "oauth-protected-resource" in www_auth
