"""API endpoints for managing MCP board access from Account page."""

import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel

from app.core.database import get_session
from app.core.deps import get_current_user
from app.auth.models import User, OAuthToken
from app.boards.service import get_boards, get_board_with_access

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mcp", tags=["mcp"])


class AddBoardRequest(BaseModel):
    board_id: str


@router.get("/connections")
def list_connections(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List active MCP connections with their shared boards."""
    tokens = session.exec(
        select(OAuthToken).where(OAuthToken.user_id == user.id)
    ).all()

    connections = []
    for token in tokens:
        board_ids = token.get_board_ids()
        boards = []
        for bid in board_ids:
            result = get_board_with_access(session, bid, user.id)
            if result:
                board, role = result
                boards.append({
                    "id": board.id,
                    "name": board.name,
                })
        connections.append({
            "id": token.id,
            "client_id": token.client_id,
            "boards": boards,
            "created_at": token.created_at.isoformat(),
            "expires_at": token.expires_at.isoformat(),
        })

    return connections


@router.post("/connections/{connection_id}/boards")
def add_board_to_connection(
    connection_id: str,
    req: AddBoardRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Add a board to an existing MCP connection."""
    token = session.get(OAuthToken, connection_id)
    if not token or token.user_id != user.id:
        raise HTTPException(status_code=404, detail="Connection not found")

    # Verify user has access to the board
    result = get_board_with_access(session, req.board_id, user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Board not found or not accessible")

    board_ids = token.get_board_ids()
    if req.board_id in board_ids:
        raise HTTPException(status_code=400, detail="Board already added")

    board_ids.append(req.board_id)
    token.set_board_ids(board_ids)
    session.add(token)
    session.commit()

    board, _ = result
    logger.info(f"Added board {req.board_id} to MCP connection {connection_id}")
    return {"added": True, "board": {"id": board.id, "name": board.name}}


@router.delete("/connections/{connection_id}/boards/{board_id}")
def remove_board_from_connection(
    connection_id: str,
    board_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Remove a board from an MCP connection."""
    token = session.get(OAuthToken, connection_id)
    if not token or token.user_id != user.id:
        raise HTTPException(status_code=404, detail="Connection not found")

    board_ids = token.get_board_ids()
    if board_id not in board_ids:
        raise HTTPException(status_code=404, detail="Board not in this connection")

    if len(board_ids) <= 1:
        raise HTTPException(status_code=400, detail="Cannot remove the last board")

    board_ids.remove(board_id)
    token.set_board_ids(board_ids)
    session.add(token)
    session.commit()

    logger.info(f"Removed board {board_id} from MCP connection {connection_id}")
    return {"removed": True}


@router.delete("/connections/{connection_id}")
def revoke_connection(
    connection_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Revoke an MCP connection entirely."""
    token = session.get(OAuthToken, connection_id)
    if not token or token.user_id != user.id:
        raise HTTPException(status_code=404, detail="Connection not found")

    session.delete(token)
    session.commit()

    logger.info(f"Revoked MCP connection {connection_id}")
    return {"revoked": True}
