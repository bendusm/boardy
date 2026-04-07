import re
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Session, select, or_
from fastapi import HTTPException

import json
from .models import (
    Board, Column, Card, Comment, Attachment,
    CardStatus, CreatedBy, BoardRole, BoardMember, BoardInvite, InviteStatus,
)
from app.auth.models import User


# Role hierarchy for permission checks
ROLE_HIERARCHY = {BoardRole.viewer: 1, BoardRole.editor: 2, BoardRole.owner: 3}


def slugify(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    slug = re.sub(r"^-+|-+$", "", slug)
    return slug


def unique_slug(session: Session, base: str) -> str:
    slug = slugify(base)
    candidate = slug
    n = 1
    while session.exec(select(Board).where(Board.slug == candidate)).first():
        candidate = f"{slug}-{n}"
        n += 1
    return candidate


DEFAULT_COLUMNS = ["Backlog", "In Progress", "Review", "Done"]


# ─── Access Control ─────────────────────────────────────────────────

def get_user_board_role(session: Session, board_id: str, user_id: str) -> Optional[BoardRole]:
    """Get user's role on a board. Returns None if no access."""
    board = session.get(Board, board_id)
    if not board:
        return None

    # Check if owner (via owner_id field for backwards compat)
    if board.owner_id == user_id:
        return BoardRole.owner

    # Check BoardMember
    member = session.exec(
        select(BoardMember).where(
            BoardMember.board_id == board_id,
            BoardMember.user_id == user_id
        )
    ).first()

    return member.role if member else None


def check_board_access(
    session: Session,
    board_id: str,
    user_id: str,
    required_role: BoardRole = BoardRole.viewer
) -> Board:
    """Check access and return Board, or raise HTTPException."""
    board = session.get(Board, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    role = get_user_board_role(session, board_id, user_id)
    if not role:
        raise HTTPException(status_code=404, detail="Board not found")

    if ROLE_HIERARCHY[role] < ROLE_HIERARCHY[required_role]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    return board


# ─── Boards ──────────────────────────────────────────────────────────

def create_board(session: Session, owner_id: str, name: str) -> Board:
    slug = unique_slug(session, name)
    board = Board(owner_id=owner_id, name=name, slug=slug)
    session.add(board)
    session.flush()  # get board.id

    for i, col_name in enumerate(DEFAULT_COLUMNS):
        col = Column(board_id=board.id, name=col_name, position=i)
        session.add(col)

    session.commit()
    session.refresh(board)
    return board


def get_boards(session: Session, user_id: str) -> list[tuple[Board, BoardRole]]:
    """Get all boards user has access to (owned + shared) with their role."""
    # Boards where user is owner
    owned = session.exec(select(Board).where(Board.owner_id == user_id)).all()
    owned_with_role = [(b, BoardRole.owner) for b in owned]

    # Boards where user is member (but not owner - avoid duplicates)
    member_boards = session.exec(
        select(Board, BoardMember.role)
        .join(BoardMember, BoardMember.board_id == Board.id)
        .where(BoardMember.user_id == user_id, Board.owner_id != user_id)
    ).all()

    return owned_with_role + list(member_boards)


def get_board(session: Session, board_id: str, owner_id: str) -> Optional[Board]:
    return session.exec(
        select(Board).where(Board.id == board_id, Board.owner_id == owner_id)
    ).first()


def get_board_with_access(
    session: Session,
    board_id: str,
    user_id: str,
    required_role: BoardRole = BoardRole.viewer
) -> Optional[tuple[Board, BoardRole]]:
    """Get board if user has required access level. Returns (board, role) or None.

    Unlike check_board_access, this doesn't raise exceptions - suitable for MCP/OAuth flows.
    """
    board = session.get(Board, board_id)
    if not board:
        return None

    role = get_user_board_role(session, board_id, user_id)
    if not role:
        return None

    if ROLE_HIERARCHY[role] < ROLE_HIERARCHY[required_role]:
        return None

    return (board, role)


def delete_board(session: Session, board: Board):
    session.delete(board)
    session.commit()


def rename_board(session: Session, board: Board, new_name: str) -> Board:
    """Rename a board."""
    board.name = new_name
    board.slug = unique_slug(session, new_name)
    session.add(board)
    session.commit()
    session.refresh(board)
    return board


# ─── Columns ─────────────────────────────────────────────────────────

def validate_column_in_board(session: Session, board_id: str, column_id: str) -> Column:
    """Validate that a column belongs to a board. Raises HTTPException if not.

    Security: Prevents IDOR attacks where attacker provides column_id from another board.
    """
    column = session.get(Column, column_id)
    if not column or column.board_id != board_id:
        raise HTTPException(status_code=404, detail="Column not found")
    return column


def get_columns(session: Session, board_id: str) -> list[Column]:
    return list(
        session.exec(select(Column).where(Column.board_id == board_id).order_by(Column.position)).all()
    )


def create_column(session: Session, board_id: str, name: str, position: int) -> Column:
    col = Column(board_id=board_id, name=name, position=position)
    session.add(col)
    session.commit()
    session.refresh(col)
    return col


def rename_column(session: Session, column: Column, name: str) -> Column:
    column.name = name
    session.add(column)
    session.commit()
    session.refresh(column)
    return column


def delete_column(session: Session, column: Column) -> None:
    """Delete a column and all its cards."""
    # Delete all cards in this column first
    cards = session.exec(select(Card).where(Card.column_id == column.id)).all()
    for card in cards:
        # Delete comments and attachments
        for comment in session.exec(select(Comment).where(Comment.card_id == card.id)).all():
            session.delete(comment)
        for attachment in session.exec(select(Attachment).where(Attachment.card_id == card.id)).all():
            session.delete(attachment)
        session.delete(card)
    session.delete(column)
    session.commit()


# ─── Cards ───────────────────────────────────────────────────────────

def validate_assignee(session: Session, board_id: str, assignee_id: Optional[str]) -> None:
    """Validate that assignee exists and has access to the board.

    Security: Prevents assigning cards to non-existent users or users without board access.
    """
    if not assignee_id:
        return  # No assignee is valid

    # AI agent is always valid
    if assignee_id == AI_AGENT_ID:
        return

    # Check user exists
    user = session.get(User, assignee_id)
    if not user:
        raise HTTPException(status_code=400, detail="Assignee not found")

    # Check user has access to this board
    role = get_user_board_role(session, board_id, assignee_id)
    if not role:
        raise HTTPException(status_code=400, detail="Assignee does not have access to this board")


def get_cards(session: Session, column_id: str) -> list[Card]:
    return list(
        session.exec(select(Card).where(Card.column_id == column_id).order_by(Card.position)).all()
    )


def get_card(session: Session, card_id: str) -> Optional[Card]:
    return session.get(Card, card_id)


def create_card(
    session: Session,
    board_id: str,
    column_id: str,
    title: str,
    description: Optional[str] = None,
    priority: str = "medium",
    color: str = "gray",
    assignee_id: Optional[str] = None,
    due_date: Optional[datetime] = None,
    labels: Optional[list[str]] = None,
    created_by: CreatedBy = CreatedBy.user,
) -> Card:
    # Security: Validate assignee has access to the board
    validate_assignee(session, board_id, assignee_id)

    card = Card(
        board_id=board_id,
        column_id=column_id,
        title=title,
        description=description,
        priority=priority,
        color=color,
        assignee_id=assignee_id,
        due_date=due_date,
        labels=json.dumps(labels) if labels else None,
        created_by=created_by,
    )
    session.add(card)
    session.commit()
    session.refresh(card)
    return card


def update_card(session: Session, card: Card, **kwargs) -> Card:
    # Security: Validate assignee if being changed
    if "assignee_id" in kwargs and kwargs["assignee_id"] is not None:
        validate_assignee(session, card.board_id, kwargs["assignee_id"])

    for key, value in kwargs.items():
        if value is not None:
            setattr(card, key, value)
    card.updated_at = datetime.now(timezone.utc)
    session.add(card)
    session.commit()
    session.refresh(card)
    return card


def move_card(session: Session, card: Card, to_column_id: str, position: int = 0) -> Card:
    """Move card to a different column.

    Security: Validates target column belongs to the same board to prevent cross-board moves.
    """
    # Security: Validate target column belongs to the same board
    target_column = session.get(Column, to_column_id)
    if not target_column or target_column.board_id != card.board_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot move card to column in different board"
        )

    card.column_id = to_column_id
    card.position = position
    card.updated_at = datetime.now(timezone.utc)
    session.add(card)
    session.commit()
    session.refresh(card)
    return card


def close_card(session: Session, card: Card, reason: Optional[str] = None) -> Card:
    card.status = CardStatus.done
    card.updated_at = datetime.now(timezone.utc)
    if reason:
        comment = Comment(card_id=card.id, author=CreatedBy.claude, text=f"Closed: {reason}")
        session.add(comment)
    session.add(card)
    session.commit()
    session.refresh(card)
    return card


def delete_card(session: Session, card: Card) -> None:
    """Permanently delete a card and its comments/attachments."""
    # Delete related comments
    session.exec(select(Comment).where(Comment.card_id == card.id)).all()
    for comment in session.exec(select(Comment).where(Comment.card_id == card.id)).all():
        session.delete(comment)
    # Delete related attachments
    for attachment in session.exec(select(Attachment).where(Attachment.card_id == card.id)).all():
        session.delete(attachment)
    session.delete(card)
    session.commit()


def archive_card(session: Session, card: Card) -> Card:
    """Soft delete - mark card as archived."""
    card.archived = True
    card.updated_at = datetime.now(timezone.utc)
    session.add(card)
    session.commit()
    session.refresh(card)
    return card


def unarchive_card(session: Session, card: Card) -> Card:
    """Restore archived card."""
    card.archived = False
    card.updated_at = datetime.now(timezone.utc)
    session.add(card)
    session.commit()
    session.refresh(card)
    return card


def duplicate_card(session: Session, card: Card, to_column_id: Optional[str] = None) -> Card:
    """Duplicate a card, optionally to a different column.

    Security: Validates target column belongs to the same board.
    """
    # Security: If target column specified, validate it belongs to the same board
    if to_column_id:
        target_column = session.get(Column, to_column_id)
        if not target_column or target_column.board_id != card.board_id:
            raise HTTPException(
                status_code=400,
                detail="Cannot duplicate card to column in different board"
            )

    new_card = Card(
        board_id=card.board_id,
        column_id=to_column_id or card.column_id,
        title=f"{card.title} (copy)",
        description=card.description,
        priority=card.priority,
        color=card.color,
        assignee_id=card.assignee_id,
        due_date=card.due_date,
        labels=card.labels,
        created_by=card.created_by,
    )
    session.add(new_card)
    session.commit()
    session.refresh(new_card)
    return new_card


def search_cards(
    session: Session,
    board_id: str,
    column_id: Optional[str] = None,
    assignee_id: Optional[str] = None,
    color: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    label: Optional[str] = None,
    created_by: Optional[str] = None,
    include_archived: bool = False,
) -> list[Card]:
    """Search cards with filters."""
    query = select(Card).where(Card.board_id == board_id)

    if not include_archived:
        query = query.where(Card.archived == False)
    if column_id:
        query = query.where(Card.column_id == column_id)
    if assignee_id:
        query = query.where(Card.assignee_id == assignee_id)
    if color:
        query = query.where(Card.color == color)
    if priority:
        query = query.where(Card.priority == priority)
    if status:
        query = query.where(Card.status == status)
    if created_by:
        query = query.where(Card.created_by == created_by)
    if label:
        # Search in JSON labels field
        query = query.where(Card.labels.contains(label))

    return list(session.exec(query.order_by(Card.position)).all())


# ─── Comments ────────────────────────────────────────────────────────

def add_comment(
    session: Session,
    card_id: str,
    text: str,
    author: CreatedBy = CreatedBy.user,
) -> Comment:
    comment = Comment(card_id=card_id, author=author, text=text)
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment


def get_comments(session: Session, card_id: str) -> list[Comment]:
    return list(session.exec(select(Comment).where(Comment.card_id == card_id)).all())


# ─── Full board (for MCP) ─────────────────────────────────────────────

# Virtual AI agent ID - used for assigning tasks to AI
AI_AGENT_ID = "ai-agent"


def get_user_name(session: Session, user_id: Optional[str]) -> Optional[str]:
    """Get user display name by ID."""
    if not user_id:
        return None
    # Handle AI agent
    if user_id == AI_AGENT_ID:
        return "AI Assistant"
    user = session.get(User, user_id)
    if user:
        return user.name or user.email.split("@")[0]
    return None


def card_to_dict(session: Session, card: Card) -> dict:
    """Convert card to dict with all fields and assignee name."""
    return {
        "id": card.id,
        "column_id": card.column_id,
        "board_id": card.board_id,
        "title": card.title,
        "description": card.description,
        "priority": card.priority.value if hasattr(card.priority, 'value') else card.priority,
        "status": card.status.value if hasattr(card.status, 'value') else card.status,
        "color": card.color.value if hasattr(card.color, 'value') else card.color,
        "position": card.position,
        "created_by": card.created_by.value if hasattr(card.created_by, 'value') else card.created_by,
        "assignee_id": card.assignee_id,
        "assignee_name": get_user_name(session, card.assignee_id),
        "due_date": card.due_date.isoformat() if card.due_date else None,
        "labels": json.loads(card.labels) if card.labels else [],
        "archived": card.archived,
        "created_at": card.created_at.isoformat(),
        "updated_at": card.updated_at.isoformat(),
    }


def get_board_full(
    session: Session,
    board_id: str,
    user_id: str,
    include_archived: bool = False
) -> dict:
    """Get full board with columns and cards. Validates user access.

    Security: Raises HTTPException instead of silent failure to ensure
    unauthorized access attempts are properly logged and handled.
    """
    board = session.get(Board, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    # Security: verify user has access to this board
    role = get_user_board_role(session, board_id, user_id)
    if not role:
        raise HTTPException(status_code=404, detail="Board not found")
    columns = get_columns(session, board_id)
    result = {
        "id": board.id,
        "name": board.name,
        "slug": board.slug,
        "my_role": role.value if hasattr(role, 'value') else role,
        "columns": [],
    }
    for col in columns:
        cards = get_cards(session, col.id)
        if not include_archived:
            cards = [c for c in cards if not c.archived]
        result["columns"].append({
            "id": col.id,
            "name": col.name,
            "position": col.position,
            "cards": [card_to_dict(session, c) for c in cards],
        })
    return result


# ─── Board Members ───────────────────────────────────────────────────

def get_board_members(session: Session, board_id: str) -> list[tuple[BoardMember, str]]:
    """Get all members with their emails."""
    members = session.exec(
        select(BoardMember, User.email)
        .join(User, User.id == BoardMember.user_id)
        .where(BoardMember.board_id == board_id)
    ).all()
    return list(members)


def add_board_member(
    session: Session,
    board_id: str,
    user_id: str,
    role: BoardRole = BoardRole.viewer
) -> BoardMember:
    """Add a user as board member."""
    member = BoardMember(board_id=board_id, user_id=user_id, role=role)
    session.add(member)
    session.commit()
    session.refresh(member)
    return member


def update_member_role(session: Session, member: BoardMember, role: BoardRole) -> BoardMember:
    """Update member's role."""
    if role == BoardRole.owner:
        raise HTTPException(status_code=400, detail="Cannot assign owner role")
    member.role = role
    session.add(member)
    session.commit()
    session.refresh(member)
    return member


def remove_board_member(session: Session, member: BoardMember) -> None:
    """Remove member from board."""
    session.delete(member)
    session.commit()


def get_member_by_id(session: Session, member_id: str) -> Optional[BoardMember]:
    return session.get(BoardMember, member_id)


# ─── Board Invites ───────────────────────────────────────────────────

def create_invite(
    session: Session,
    board_id: str,
    email: str,
    role: BoardRole,
    invited_by: str
) -> BoardInvite:
    """Create an invitation."""
    invite = BoardInvite(
        board_id=board_id,
        email=email.lower(),
        role=role,
        invited_by=invited_by,
    )
    session.add(invite)
    session.commit()
    session.refresh(invite)
    return invite


def get_pending_invites(session: Session, board_id: str) -> list[BoardInvite]:
    """Get all pending invites for a board."""
    return list(session.exec(
        select(BoardInvite).where(
            BoardInvite.board_id == board_id,
            BoardInvite.status == InviteStatus.pending
        )
    ).all())


def get_invite_by_id(session: Session, invite_id: str) -> Optional[BoardInvite]:
    return session.get(BoardInvite, invite_id)


def get_invite_by_token(session: Session, token: str) -> Optional[BoardInvite]:
    return session.exec(
        select(BoardInvite).where(BoardInvite.token == token)
    ).first()


def get_user_pending_invites(session: Session, email: str) -> list[tuple[BoardInvite, str, str]]:
    """Get all pending invites for a user's email with board name and inviter email."""
    return list(session.exec(
        select(BoardInvite, Board.name, User.email)
        .join(Board, Board.id == BoardInvite.board_id)
        .join(User, User.id == BoardInvite.invited_by)
        .where(
            BoardInvite.email == email.lower(),
            BoardInvite.status == InviteStatus.pending,
            BoardInvite.expires_at > datetime.now(timezone.utc)
        )
    ).all())


def accept_invite(session: Session, invite: BoardInvite, user_id: str) -> BoardMember:
    """Accept an invite and create membership."""
    invite.status = InviteStatus.accepted
    invite.accepted_at = datetime.now(timezone.utc)
    session.add(invite)

    member = BoardMember(
        board_id=invite.board_id,
        user_id=user_id,
        role=invite.role
    )
    session.add(member)
    session.commit()
    session.refresh(member)
    return member


def decline_invite(session: Session, invite: BoardInvite) -> None:
    """Decline an invite."""
    invite.status = InviteStatus.declined
    session.add(invite)
    session.commit()


def cancel_invite(session: Session, invite: BoardInvite) -> None:
    """Cancel/delete an invite."""
    session.delete(invite)
    session.commit()


def check_existing_invite(session: Session, board_id: str, email: str) -> Optional[BoardInvite]:
    """Check if pending invite already exists."""
    return session.exec(
        select(BoardInvite).where(
            BoardInvite.board_id == board_id,
            BoardInvite.email == email.lower(),
            BoardInvite.status == InviteStatus.pending
        )
    ).first()


def check_existing_member_by_email(session: Session, board_id: str, email: str) -> bool:
    """Check if user with this email is already a member."""
    user = session.exec(select(User).where(User.email == email.lower())).first()
    if not user:
        return False
    member = session.exec(
        select(BoardMember).where(
            BoardMember.board_id == board_id,
            BoardMember.user_id == user.id
        )
    ).first()
    return member is not None
