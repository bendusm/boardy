from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional
from enum import Enum
from app.core.ulid import ulid_field


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class CardStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    blocked = "blocked"
    done = "done"


class CreatedBy(str, Enum):
    user = "user"
    claude = "claude"


# ─── Board ───────────────────────────────────────────────────────────

class Board(SQLModel, table=True):
    __tablename__ = "boards"

    id: str = Field(default_factory=ulid_field, primary_key=True)
    owner_id: str = Field(index=True)
    name: str
    slug: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ─── Column ──────────────────────────────────────────────────────────

class Column(SQLModel, table=True):
    __tablename__ = "columns"

    id: str = Field(default_factory=ulid_field, primary_key=True)
    board_id: str = Field(index=True)
    name: str
    position: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ─── Card ────────────────────────────────────────────────────────────

class Card(SQLModel, table=True):
    __tablename__ = "cards"

    id: str = Field(default_factory=ulid_field, primary_key=True)
    column_id: str = Field(index=True)
    board_id: str = Field(index=True)
    title: str
    description: Optional[str] = None          # markdown
    priority: Priority = Priority.medium
    status: CardStatus = CardStatus.open
    position: int = 0
    created_by: CreatedBy = CreatedBy.user
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ─── Comment ─────────────────────────────────────────────────────────

class Comment(SQLModel, table=True):
    __tablename__ = "comments"

    id: str = Field(default_factory=ulid_field, primary_key=True)
    card_id: str = Field(index=True)
    author: CreatedBy = CreatedBy.user
    text: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ─── Attachment ──────────────────────────────────────────────────────

class Attachment(SQLModel, table=True):
    __tablename__ = "attachments"

    id: str = Field(default_factory=ulid_field, primary_key=True)
    card_id: str = Field(index=True)
    filename: str
    r2_key: str
    size_bytes: int = 0
    uploaded_by: CreatedBy = CreatedBy.user
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ─── Pydantic schemas (request/response) ─────────────────────────────

class BoardCreate(SQLModel):
    name: str


class BoardRead(SQLModel):
    id: str
    name: str
    slug: str
    owner_id: str
    created_at: datetime


class ColumnCreate(SQLModel):
    name: str
    position: int = 0


class ColumnRead(SQLModel):
    id: str
    board_id: str
    name: str
    position: int


class CardCreate(SQLModel):
    title: str
    description: Optional[str] = None
    priority: Priority = Priority.medium


class CardUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Priority] = None
    status: Optional[CardStatus] = None


class CardRead(SQLModel):
    id: str
    column_id: str
    board_id: str
    title: str
    description: Optional[str]
    priority: Priority
    status: CardStatus
    position: int
    created_by: CreatedBy
    created_at: datetime
    updated_at: datetime


class CardMove(SQLModel):
    to_column_id: str
    position: int = 0


class CommentCreate(SQLModel):
    text: str


class CommentRead(SQLModel):
    id: str
    card_id: str
    author: CreatedBy
    text: str
    created_at: datetime


class BoardFull(SQLModel):
    """Полная доска с колонками и карточками — для MCP get_board."""
    id: str
    name: str
    slug: str
    columns: list[dict]
