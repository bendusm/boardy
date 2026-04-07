"""FastMCP server for Boardy - Claude Desktop integration."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
import logging

from fastmcp import FastMCP
from fastmcp.server.auth import OAuthProvider, AccessToken
from fastmcp.server.dependencies import get_http_request
from sqlmodel import Session, select

from app.core.database import engine
from app.core.config import settings
from app.auth.models import OAuthToken
from app.boards.models import CreatedBy, Attachment, BoardRole
from app.boards import service

logger = logging.getLogger(__name__)

# ─── MCP Server Setup ───────────────────────────────────────────────────

MCP_INSTRUCTIONS = """
Ты подключён к Kanban-доске пользователя Boardy.
Правила:
— Если в разговоре обсуждается задача — проверь, есть ли карточка. Если нет — создай.
— Если задача завершена — переведи карточку в Done.
— Если обнаружен блокер — добавь комментарий и смени статус на Blocked.
— После каждого git push/merge с упоминанием карточки — переводи её в Done.
— Никогда не оставляй обсуждённое невнесённым в доску.
"""


class BoardyOAuthProvider(OAuthProvider):
    """Custom OAuth provider that validates tokens against our database."""

    async def verify_token(self, token: str) -> AccessToken | None:
        """Verify a bearer token against our database."""
        with Session(engine) as session:
            oauth_token = session.exec(
                select(OAuthToken).where(OAuthToken.access_token == token)
            ).first()

            if not oauth_token:
                logger.warning(f"Token not found in database")
                return None

            # Handle timezone-naive datetime from DB
            expires_at = oauth_token.expires_at
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)

            if expires_at < datetime.now(timezone.utc):
                logger.warning(f"Token expired")
                return None

            # Return AccessToken with scopes
            return AccessToken(
                token=token,
                client_id=oauth_token.client_id,
                scopes=oauth_token.scope.split() if oauth_token.scope else [],
                expires_at=int(expires_at.timestamp()),
            )


# OAuth provider with custom token verification
oauth_provider = BoardyOAuthProvider(
    base_url=settings.app_url,
    issuer_url=settings.app_url,
    required_scopes=["board:read", "board:write"],
)

mcp = FastMCP(
    name="Boardy",
    instructions=MCP_INSTRUCTIONS,
    auth=oauth_provider,
)


# ─── Authentication ─────────────────────────────────────────────────────

@dataclass
class MCPContext:
    """Context extracted from OAuth token."""
    user_id: str
    board_ids: list[str]
    scopes: list[str]
    _session_roles: dict  # board_id -> role cache

    @property
    def board_id(self) -> str:
        """Primary board (backward compat)."""
        return self.board_ids[0] if self.board_ids else ""

    def get_role(self, board_id: str) -> BoardRole | None:
        return self._session_roles.get(board_id)

    def check_board_access(self, board_id: str) -> BoardRole:
        if board_id not in self.board_ids:
            raise ValueError(f"Board {board_id} not accessible with this token")
        role = self.get_role(board_id)
        if not role:
            raise ValueError(f"No access to board {board_id}")
        return role


def get_mcp_context() -> MCPContext:
    """Extract user_id, board_ids, and scopes from Bearer token."""
    request = get_http_request()
    auth_header = request.headers.get("authorization", "")

    if not auth_header.lower().startswith("bearer "):
        raise ValueError("Missing or invalid Authorization header")

    token = auth_header[7:]  # Strip "Bearer "

    with Session(engine) as session:
        oauth_token = session.exec(
            select(OAuthToken).where(
                OAuthToken.access_token == token,
                OAuthToken.expires_at > datetime.now(timezone.utc)
            )
        ).first()

        if not oauth_token:
            raise ValueError("Invalid or expired token")

        board_ids = oauth_token.get_board_ids()

        # Get user's role on each board
        roles = {}
        for bid in board_ids:
            role = service.get_user_board_role(session, bid, oauth_token.user_id)
            if role:
                roles[bid] = role

        if not roles:
            raise ValueError("No access to any boards")

        scopes = oauth_token.scope.split() if oauth_token.scope else []

        return MCPContext(
            user_id=oauth_token.user_id,
            board_ids=list(roles.keys()),
            scopes=scopes,
            _session_roles=roles,
        )


def require_editor(ctx: MCPContext, board_id: str) -> None:
    """Raise if user is not at least editor on the given board."""
    role = ctx.get_role(board_id)
    if role == BoardRole.viewer:
        raise ValueError("Viewers cannot perform this action")


def require_write_scope(ctx: MCPContext) -> None:
    """Raise if token doesn't have board:write scope."""
    if "board:write" not in ctx.scopes:
        raise ValueError("This operation requires board:write scope")


# ─── MCP Tools ──────────────────────────────────────────────────────────

@mcp.tool(annotations={"readOnlyHint": True})
def list_boards() -> list[dict]:
    """List boards accessible via current token.

    Returns all boards this token is authorized for.
    """
    ctx = get_mcp_context()
    with Session(engine) as session:
        results = []
        for bid in ctx.board_ids:
            board_result = service.get_board_with_access(session, bid, ctx.user_id)
            if board_result:
                board, _ = board_result
                results.append({"id": board.id, "name": board.name, "slug": board.slug})
        return results


@mcp.tool(annotations={"readOnlyHint": True})
def get_board(board_id: str) -> dict:
    """Get full board with columns and cards.

    Args:
        board_id: The board ID to retrieve

    Returns the complete board structure with nested columns and cards.
    """
    ctx = get_mcp_context()
    ctx.check_board_access(board_id)
    with Session(engine) as session:
        board_result = service.get_board_with_access(session, board_id, ctx.user_id)
        if not board_result:
            raise ValueError(f"Board {board_id} not found or not accessible")
        return service.get_board_full(session, board_id, ctx.user_id)


@mcp.tool(annotations={"destructiveHint": True})
def delete_board(board_id: str) -> dict:
    """Delete a board permanently.

    WARNING: This action cannot be undone. Only board owners can delete boards.
    All columns, cards, comments, and attachments will be permanently deleted.

    Args:
        board_id: The board to delete

    Returns confirmation of deletion.
    """
    ctx = get_mcp_context()
    role = ctx.check_board_access(board_id)
    with Session(engine) as session:
        # Security: Only owners can delete boards
        if role != BoardRole.owner:
            raise ValueError("Only board owners can delete boards")

        require_write_scope(ctx)

        board_result = service.get_board_with_access(session, board_id, ctx.user_id, BoardRole.owner)
        if not board_result:
            raise ValueError(f"Board {board_id} not found or you don't have owner permissions")

        board, _ = board_result
        board_name = board.name
        service.delete_board(session, board)
        logger.info(f"MCP deleted board {board_id}")
        return {
            "deleted": True,
            "board_id": board_id,
            "name": board_name,
        }


@mcp.tool(annotations={"destructiveHint": False})
def create_card(
    board_id: str,
    column_id: str,
    title: str,
    description: Optional[str] = None,
    priority: str = "medium"
) -> dict:
    """Create a new card on the board.

    Args:
        board_id: The board to create the card on
        column_id: The column to place the card in
        title: Card title
        description: Optional card description (markdown supported)
        priority: Priority level (low, medium, high, critical)

    Returns the created card details.
    """
    ctx = get_mcp_context()
    ctx.check_board_access(board_id)
    require_editor(ctx, board_id)
    require_write_scope(ctx)
    with Session(engine) as session:
        board_result = service.get_board_with_access(session, board_id, ctx.user_id)
        if not board_result:
            raise ValueError(f"Board {board_id} not found or not accessible")

        # Security: Verify column belongs to this board
        columns = service.get_columns(session, board_id)
        valid_column_ids = {col.id for col in columns}
        if column_id not in valid_column_ids:
            raise ValueError(f"Column {column_id} not found in board {board_id}")

        card = service.create_card(
            session,
            board_id=board_id,
            column_id=column_id,
            title=title,
            description=description,
            priority=priority,
            created_by=CreatedBy.claude,
        )
        logger.info(f"MCP created card {card.id} on board {board_id}")
        return {
            "id": card.id,
            "title": card.title,
            "column_id": card.column_id,
            "priority": card.priority.value if hasattr(card.priority, 'value') else card.priority,
            "status": card.status.value if hasattr(card.status, 'value') else card.status,
        }


@mcp.tool(annotations={"destructiveHint": False})
def update_card(
    card_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    color: Optional[str] = None,
    assignee_id: Optional[str] = None,
    due_date: Optional[str] = None,
    labels: Optional[list[str]] = None
) -> dict:
    """Update an existing card.

    Args:
        card_id: The card to update
        title: New title (optional)
        description: New description (optional)
        priority: New priority - low, medium, high, critical (optional)
        status: New status - open, in_progress, blocked, done (optional)
        color: New color - gray, red, orange, yellow, green, blue, purple, pink (optional)
        assignee_id: User ID to assign card to (optional, use empty string to unassign)
        due_date: Due date in ISO format YYYY-MM-DD (optional, use empty string to clear)
        labels: List of label strings (optional)

    Returns the updated card details.
    """
    import json
    from datetime import datetime as dt

    ctx = get_mcp_context()
    with Session(engine) as session:
        card = service.get_card(session, card_id)
        if not card:
            raise ValueError(f"Card {card_id} not found")

        ctx.check_board_access(card.board_id)
        require_editor(ctx, card.board_id)
        require_write_scope(ctx)

        # Handle special cases
        update_kwargs = {}
        if title is not None:
            update_kwargs['title'] = title
        if description is not None:
            update_kwargs['description'] = description
        if priority is not None:
            update_kwargs['priority'] = priority
        if status is not None:
            update_kwargs['status'] = status
        if color is not None:
            update_kwargs['color'] = color
        if assignee_id is not None:
            update_kwargs['assignee_id'] = assignee_id if assignee_id else None
        if due_date is not None:
            update_kwargs['due_date'] = dt.fromisoformat(due_date) if due_date else None
        if labels is not None:
            update_kwargs['labels'] = json.dumps(labels) if labels else None

        updated = service.update_card(session, card, **update_kwargs)
        logger.info(f"MCP updated card {card_id}")
        return service.card_to_dict(session, updated)


@mcp.tool(annotations={"destructiveHint": False})
def move_card(card_id: str, to_column_id: str) -> dict:
    """Move a card to a different column.

    Args:
        card_id: The card to move
        to_column_id: Target column ID

    Returns the moved card details.
    """
    ctx = get_mcp_context()
    with Session(engine) as session:
        card = service.get_card(session, card_id)
        if not card:
            raise ValueError(f"Card {card_id} not found")

        ctx.check_board_access(card.board_id)
        require_editor(ctx, card.board_id)
        require_write_scope(ctx)

        # Security: Verify target column belongs to the same board
        columns = service.get_columns(session, card.board_id)
        valid_column_ids = {col.id for col in columns}
        if to_column_id not in valid_column_ids:
            raise ValueError(f"Column {to_column_id} not found in board")

        moved = service.move_card(session, card, to_column_id, position=0)
        logger.info(f"MCP moved card {card_id} to column {to_column_id}")
        return {
            "id": moved.id,
            "title": moved.title,
            "column_id": moved.column_id,
        }


@mcp.tool(annotations={"destructiveHint": False})
def add_comment(card_id: str, text: str) -> dict:
    """Add a comment to a card.

    Args:
        card_id: The card to comment on
        text: Comment text

    Returns the created comment details.
    """
    ctx = get_mcp_context()
    require_write_scope(ctx)
    with Session(engine) as session:
        card = service.get_card(session, card_id)
        if not card:
            raise ValueError(f"Card {card_id} not found")

        ctx.check_board_access(card.board_id)

        board_result = service.get_board_with_access(session, card.board_id, ctx.user_id)
        if not board_result:
            raise ValueError("Card not accessible")

        comment = service.add_comment(
            session,
            card_id=card_id,
            text=text,
            author=CreatedBy.claude,
        )
        logger.info(f"MCP added comment to card {card_id}")
        return {
            "id": comment.id,
            "card_id": comment.card_id,
            "text": comment.text,
            "author": comment.author.value if hasattr(comment.author, 'value') else comment.author,
        }


@mcp.tool(annotations={"destructiveHint": False})
def attach_file(card_id: str, file_url: str, filename: str) -> dict:
    """Attach a file to a card via URL.

    Args:
        card_id: The card to attach the file to
        file_url: URL of the file
        filename: Display name of the file

    Returns the created attachment details.
    """
    ctx = get_mcp_context()
    with Session(engine) as session:
        card = service.get_card(session, card_id)
        if not card:
            raise ValueError(f"Card {card_id} not found")

        ctx.check_board_access(card.board_id)
        require_editor(ctx, card.board_id)
        require_write_scope(ctx)

        attachment = Attachment(
            card_id=card_id,
            filename=filename,
            r2_key=file_url,
            uploaded_by=CreatedBy.claude,
        )
        session.add(attachment)
        session.commit()
        session.refresh(attachment)

        logger.info(f"MCP attached file to card {card_id}")
        return {
            "id": attachment.id,
            "card_id": attachment.card_id,
            "filename": attachment.filename,
            "url": attachment.r2_key,
        }


@mcp.tool(annotations={"destructiveHint": False})
def close_card(card_id: str, reason: Optional[str] = None) -> dict:
    """Close a card (mark as done).

    Use this when a task is completed, e.g., after a successful git push/merge.

    Args:
        card_id: The card to close
        reason: Optional reason for closing (will be added as comment)

    Returns the closed card details.
    """
    ctx = get_mcp_context()
    with Session(engine) as session:
        card = service.get_card(session, card_id)
        if not card:
            raise ValueError(f"Card {card_id} not found")

        ctx.check_board_access(card.board_id)
        require_editor(ctx, card.board_id)
        require_write_scope(ctx)

        closed = service.close_card(session, card, reason=reason)
        logger.info(f"MCP closed card {card_id}")
        return service.card_to_dict(session, closed)


@mcp.tool(annotations={"destructiveHint": True})
def delete_card(card_id: str) -> dict:
    """Permanently delete a card.

    WARNING: This action cannot be undone. Consider using archive_card instead.

    Args:
        card_id: The card to delete

    Returns confirmation of deletion.
    """
    ctx = get_mcp_context()
    with Session(engine) as session:
        card = service.get_card(session, card_id)
        if not card:
            raise ValueError(f"Card {card_id} not found")

        ctx.check_board_access(card.board_id)
        require_editor(ctx, card.board_id)
        require_write_scope(ctx)

        card_title = card.title
        service.delete_card(session, card)
        logger.info(f"MCP deleted card {card_id}")
        return {
            "deleted": True,
            "card_id": card_id,
            "title": card_title,
        }


@mcp.tool(annotations={"destructiveHint": False})
def archive_card(card_id: str) -> dict:
    """Archive a card (soft delete).

    Archived cards are hidden from the board but can be restored.

    Args:
        card_id: The card to archive

    Returns the archived card details.
    """
    ctx = get_mcp_context()
    with Session(engine) as session:
        card = service.get_card(session, card_id)
        if not card:
            raise ValueError(f"Card {card_id} not found")

        ctx.check_board_access(card.board_id)
        require_editor(ctx, card.board_id)
        require_write_scope(ctx)

        archived = service.archive_card(session, card)
        logger.info(f"MCP archived card {card_id}")
        return service.card_to_dict(session, archived)


@mcp.tool(annotations={"destructiveHint": False})
def duplicate_card(card_id: str, to_column_id: Optional[str] = None) -> dict:
    """Duplicate a card.

    Creates a copy of the card with "(copy)" suffix in title.

    Args:
        card_id: The card to duplicate
        to_column_id: Target column ID (optional, defaults to same column)

    Returns the new card details.
    """
    ctx = get_mcp_context()
    with Session(engine) as session:
        card = service.get_card(session, card_id)
        if not card:
            raise ValueError(f"Card {card_id} not found")

        ctx.check_board_access(card.board_id)
        require_editor(ctx, card.board_id)
        require_write_scope(ctx)

        new_card = service.duplicate_card(session, card, to_column_id)
        logger.info(f"MCP duplicated card {card_id} -> {new_card.id}")
        return service.card_to_dict(session, new_card)


@mcp.tool(annotations={"readOnlyHint": True})
def search_cards(
    board_id: str,
    column_id: Optional[str] = None,
    assignee_id: Optional[str] = None,
    color: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    label: Optional[str] = None,
    created_by: Optional[str] = None,
    include_archived: bool = False,
) -> list[dict]:
    """Search and filter cards on a board.

    Args:
        board_id: The board to search
        column_id: Filter by column ID (optional)
        assignee_id: Filter by assignee user ID (optional)
        color: Filter by color - gray, red, orange, yellow, green, blue, purple, pink (optional)
        priority: Filter by priority - low, medium, high, critical (optional)
        status: Filter by status - open, in_progress, blocked, done (optional)
        label: Filter by label (optional)
        created_by: Filter by creator - "user" or "claude" (optional)
        include_archived: Include archived cards (default False)

    Returns list of matching cards.
    """
    ctx = get_mcp_context()
    ctx.check_board_access(board_id)
    with Session(engine) as session:
        board_result = service.get_board_with_access(session, board_id, ctx.user_id)
        if not board_result:
            raise ValueError(f"Board {board_id} not found or not accessible")

        cards = service.search_cards(
            session,
            board_id=board_id,
            column_id=column_id,
            assignee_id=assignee_id,
            color=color,
            priority=priority,
            status=status,
            label=label,
            created_by=created_by,
            include_archived=include_archived,
        )
        logger.info(f"MCP searched cards on board {board_id}, found {len(cards)}")
        return [service.card_to_dict(session, c) for c in cards]


@mcp.tool(annotations={"readOnlyHint": True})
def list_users(board_id: str) -> list[dict]:
    """List all users who have access to a board.

    Useful for getting user IDs for assignee_id filter.

    Args:
        board_id: The board ID

    Returns list of users with id, name, email, and role.
    """
    ctx = get_mcp_context()
    ctx.check_board_access(board_id)
    with Session(engine) as session:
        # Get all board members
        from app.auth.models import User
        members = service.get_board_members(session, board_id)
        users = []
        for member, email in members:
            user = session.get(User, member.user_id)
            if user:
                users.append({
                    "id": user.id,
                    "name": user.name or user.email.split("@")[0],
                    "email": user.email,
                    "role": member.role.value if hasattr(member.role, 'value') else member.role,
                })

        return users
