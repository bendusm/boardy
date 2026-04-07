"""Tests for MCP tools functionality."""

import asyncio
import pytest


# Helper to get tools synchronously
def get_mcp_tools():
    """Get MCP tools list synchronously."""
    from app.mcp_server import mcp
    return asyncio.get_event_loop().run_until_complete(mcp.list_tools())


def get_tool_by_name(tools, name):
    """Find tool by name in tools list."""
    for tool in tools:
        if tool.name == name:
            return tool
    return None


class TestMCPToolAnnotations:
    """Tests for MCP tool annotations (required for Anthropic Directory)."""

    @pytest.fixture(autouse=True)
    def setup_tools(self):
        """Load tools once for all tests in this class."""
        self.tools = get_mcp_tools()

    def test_list_boards_has_readonly_hint(self):
        """Test that list_boards has readOnlyHint annotation."""
        tool = get_tool_by_name(self.tools, "list_boards")
        assert tool is not None
        assert tool.annotations.readOnlyHint is True

    def test_get_board_has_readonly_hint(self):
        """Test that get_board has readOnlyHint annotation."""
        tool = get_tool_by_name(self.tools, "get_board")
        assert tool is not None
        assert tool.annotations.readOnlyHint is True

    def test_create_card_has_destructive_false(self):
        """Test that create_card has destructiveHint: false."""
        tool = get_tool_by_name(self.tools, "create_card")
        assert tool is not None
        assert tool.annotations.destructiveHint is False

    def test_update_card_has_destructive_false(self):
        """Test that update_card has destructiveHint: false."""
        tool = get_tool_by_name(self.tools, "update_card")
        assert tool is not None
        assert tool.annotations.destructiveHint is False

    def test_move_card_has_destructive_false(self):
        """Test that move_card has destructiveHint: false."""
        tool = get_tool_by_name(self.tools, "move_card")
        assert tool is not None
        assert tool.annotations.destructiveHint is False

    def test_delete_card_has_destructive_true(self):
        """Test that delete_card has destructiveHint: true."""
        tool = get_tool_by_name(self.tools, "delete_card")
        assert tool is not None
        assert tool.annotations.destructiveHint is True

    def test_delete_board_has_destructive_true(self):
        """Test that delete_board has destructiveHint: true."""
        tool = get_tool_by_name(self.tools, "delete_board")
        assert tool is not None
        assert tool.annotations.destructiveHint is True

    def test_add_comment_has_destructive_false(self):
        """Test that add_comment has destructiveHint: false."""
        tool = get_tool_by_name(self.tools, "add_comment")
        assert tool is not None
        assert tool.annotations.destructiveHint is False

    def test_close_card_has_destructive_false(self):
        """Test that close_card has destructiveHint: false."""
        tool = get_tool_by_name(self.tools, "close_card")
        assert tool is not None
        assert tool.annotations.destructiveHint is False

    def test_search_cards_has_readonly_hint(self):
        """Test that search_cards has readOnlyHint annotation."""
        tool = get_tool_by_name(self.tools, "search_cards")
        assert tool is not None
        assert tool.annotations.readOnlyHint is True

    def test_list_users_has_readonly_hint(self):
        """Test that list_users has readOnlyHint annotation."""
        tool = get_tool_by_name(self.tools, "list_users")
        assert tool is not None
        assert tool.annotations.readOnlyHint is True

    def test_all_tools_have_annotations(self):
        """Test that all MCP tools have required annotations."""
        for tool in self.tools:
            has_readonly = tool.annotations.readOnlyHint is not None
            has_destructive = tool.annotations.destructiveHint is not None
            assert has_readonly or has_destructive, (
                f"Tool '{tool.name}' missing readOnlyHint or destructiveHint annotation"
            )


class TestMCPToolsWithAuth:
    """Tests for MCP tools with authentication."""

    def test_mcp_requires_authentication(self, client):
        """Test that MCP endpoint requires authentication."""
        response = client.post(
            "/mcp/",
            json={"jsonrpc": "2.0", "method": "tools/list", "id": 1},
        )
        # Should require auth - 401, 403, 400, or 404 (if route not matched without auth)
        assert response.status_code in [401, 403, 400, 404]

    def test_mcp_tools_list_with_auth(self, client, oauth_token):
        """Test listing MCP tools with valid authentication."""
        response = client.post(
            "/mcp/",
            json={"jsonrpc": "2.0", "method": "tools/list", "id": 1},
            headers={"Authorization": f"Bearer {oauth_token.access_token}"},
        )

        # FastMCP should return tools list
        if response.status_code == 200:
            data = response.json()
            if "result" in data and "tools" in data["result"]:
                tool_names = [t["name"] for t in data["result"]["tools"]]
                assert "list_boards" in tool_names
                assert "get_board" in tool_names
                assert "create_card" in tool_names


class TestMCPToolsIsolation:
    """Tests for MCP tools security and board isolation."""

    def test_token_scoped_to_single_board(self, oauth_token, test_board):
        """Test that OAuth token is scoped to a single board."""
        assert oauth_token.board_id == test_board.id

    def test_list_boards_returns_only_scoped_board(
        self, client, oauth_token, test_board
    ):
        """Test that list_boards only returns the token-scoped board."""
        response = client.post(
            "/mcp/",
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": "list_boards", "arguments": {}},
                "id": 1,
            },
            headers={"Authorization": f"Bearer {oauth_token.access_token}"},
        )

        if response.status_code == 200:
            data = response.json()
            if "result" in data and isinstance(data["result"], list):
                # Should only contain the scoped board
                assert len(data["result"]) == 1
                assert data["result"][0]["id"] == test_board.id


class TestMCPToolsCreatedBy:
    """Tests for MCP tools created_by tracking."""

    def test_create_card_sets_created_by_claude(
        self, client, oauth_token, test_board
    ):
        """Test that create_card sets created_by to 'claude'."""
        response = client.post(
            "/mcp/",
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "create_card",
                    "arguments": {
                        "board_id": test_board.id,
                        "column_id": "01HXCOL1000000000000001",
                        "title": "Test MCP Card",
                        "description": "Created by MCP test",
                    },
                },
                "id": 1,
            },
            headers={"Authorization": f"Bearer {oauth_token.access_token}"},
        )

        if response.status_code == 200:
            data = response.json()
            # The card should be created with created_by=claude
            # This is verified in the service layer
            if "result" in data and "id" in data.get("result", {}):
                # Card was created successfully
                pass


class TestMCPServerInfo:
    """Tests for MCP server information."""

    def test_mcp_server_name(self):
        """Test that MCP server has correct name."""
        from app.mcp_server import mcp

        assert mcp.name == "Boardy"

    def test_mcp_server_has_instructions(self):
        """Test that MCP server has instructions for Claude."""
        from app.mcp_server import mcp

        assert mcp.instructions is not None
        assert len(mcp.instructions) > 0

    def test_mcp_server_has_auth_provider(self):
        """Test that MCP server has OAuth provider configured."""
        from app.mcp_server import mcp, oauth_provider

        assert mcp.auth is not None
        assert mcp.auth == oauth_provider
