import re
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Session, select

from .models import (
    Board, Column, Card, Comment, Attachment,
    CardStatus, CreatedBy,
)
from app.core.ulid import ulid_field


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


def get_boards(session: Session, owner_id: str) -> list[Board]:
    return list(session.exec(select(Board).where(Board.owner_id == owner_id)).all())


def get_board(session: Session, board_id: str, owner_id: str) -> Optional[Board]:
    return session.exec(
        select(Board).where(Board.id == board_id, Board.owner_id == owner_id)
    ).first()


def delete_board(session: Session, board: Board):
    session.delete(board)
    session.commit()


# ─── Columns ─────────────────────────────────────────────────────────

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


# ─── Cards ───────────────────────────────────────────────────────────

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
    created_by: CreatedBy = CreatedBy.user,
) -> Card:
    card = Card(
        board_id=board_id,
        column_id=column_id,
        title=title,
        description=description,
        priority=priority,
        created_by=created_by,
    )
    session.add(card)
    session.commit()
    session.refresh(card)
    return card


def update_card(session: Session, card: Card, **kwargs) -> Card:
    for key, value in kwargs.items():
        if value is not None:
            setattr(card, key, value)
    card.updated_at = datetime.now(timezone.utc)
    session.add(card)
    session.commit()
    session.refresh(card)
    return card


def move_card(session: Session, card: Card, to_column_id: str, position: int = 0) -> Card:
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

def get_board_full(session: Session, board_id: str) -> dict:
    board = session.get(Board, board_id)
    if not board:
        return {}
    columns = get_columns(session, board_id)
    result = {
        "id": board.id,
        "name": board.name,
        "slug": board.slug,
        "columns": [],
    }
    for col in columns:
        cards = get_cards(session, col.id)
        result["columns"].append({
            "id": col.id,
            "name": col.name,
            "position": col.position,
            "cards": [
                {
                    "id": c.id,
                    "title": c.title,
                    "description": c.description,
                    "priority": c.priority,
                    "status": c.status,
                    "position": c.position,
                    "created_by": c.created_by,
                }
                for c in cards
            ],
        })
    return result
