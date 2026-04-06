"""FastMCP server for Boardy - Claude Desktop integration."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
import logging

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_request
from sqlmodel import Session, select

from app.core.database import engine
from app.auth.models import OAuthToken
from app.boards.models import CreatedBy, Attachment
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

mcp = FastMCP(
    name="Boardy",
    instructions=MCP_INSTRUCTIONS,
)


# ─── Authentication ─────────────────────────────────────────────────────

@dataclass
class MCPContext:
    """Context extracted from OAuth token."""
    user_id: str
    board_id: str


def get_mcp_context() -> MCPContext:
    """Extract user_id and board_id from Bearer token."""
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

        return MCPContext(
            user_id=oauth_token.user_id,
            board_id=oauth_token.board_id,
        )


# ─── MCP Tools ──────────────────────────────────────────────────────────

@mcp.tool(annotations={"readOnlyHint": True})
def list_boards() -> list[dict]:
    """List all boards owned by the current user.

    Returns a list of boards with their id, name, and slug.
    """
    ctx = get_mcp_context()
    with Session(engine) as session:
        boards = service.get_boards(session, ctx.user_id)
        return [
            {"id": b.id, "name": b.name, "slug": b.slug}
            for b in boards
        ]


@mcp.tool(annotations={"readOnlyHint": True})
def get_board(board_id: str) -> dict:
    """Get full board with columns and cards.

    Args:
        board_id: The board ID to retrieve

    Returns the complete board structure with nested columns and cards.
    """
    ctx = get_mcp_context()
    with Session(engine) as session:
        board = service.get_board(session, board_id, ctx.user_id)
        if not board:
            raise ValueError(f"Board {board_id} not found or not accessible")
        return service.get_board_full(session, board_id)


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
    with Session(engine) as session:
        board = service.get_board(session, board_id, ctx.user_id)
        if not board:
            raise ValueError(f"Board {board_id} not found or not accessible")

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
    priority: Optional[str] = None
) -> dict:
    """Update an existing card.

    Args:
        card_id: The card to update
        title: New title (optional)
        description: New description (optional)
        priority: New priority - low, medium, high, critical (optional)

    Returns the updated card details.
    """
    ctx = get_mcp_context()
    with Session(engine) as session:
        card = service.get_card(session, card_id)
        if not card:
            raise ValueError(f"Card {card_id} not found")

        board = service.get_board(session, card.board_id, ctx.user_id)
        if not board:
            raise ValueError("Card not accessible")

        updated = service.update_card(
            session, card,
            title=title,
            description=description,
            priority=priority,
        )
        logger.info(f"MCP updated card {card_id}")
        return {
            "id": updated.id,
            "title": updated.title,
            "description": updated.description,
            "priority": updated.priority.value if hasattr(updated.priority, 'value') else updated.priority,
        }


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

        board = service.get_board(session, card.board_id, ctx.user_id)
        if not board:
            raise ValueError("Card not accessible")

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
    with Session(engine) as session:
        card = service.get_card(session, card_id)
        if not card:
            raise ValueError(f"Card {card_id} not found")

        board = service.get_board(session, card.board_id, ctx.user_id)
        if not board:
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

        board = service.get_board(session, card.board_id, ctx.user_id)
        if not board:
            raise ValueError("Card not accessible")

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

        board = service.get_board(session, card.board_id, ctx.user_id)
        if not board:
            raise ValueError("Card not accessible")

        closed = service.close_card(session, card, reason=reason)
        logger.info(f"MCP closed card {card_id}")
        return {
            "id": closed.id,
            "title": closed.title,
            "status": closed.status.value if hasattr(closed.status, 'value') else closed.status,
        }
