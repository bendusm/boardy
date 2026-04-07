from sqlmodel import SQLModel, Field, UniqueConstraint
from datetime import datetime, timezone, timedelta
from typing import Optional
from enum import Enum
import secrets
from pydantic import EmailStr
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


class CardColor(str, Enum):
    gray = "gray"
    red = "red"
    orange = "orange"
    yellow = "yellow"
    green = "green"
    blue = "blue"
    purple = "purple"
    pink = "pink"


class CreatedBy(str, Enum):
    user = "user"
    claude = "claude"


class BoardRole(str, Enum):
    owner = "owner"
    editor = "editor"
    viewer = "viewer"


class InviteStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"


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
    color: CardColor = CardColor.gray
    position: int = 0
    created_by: CreatedBy = CreatedBy.user
    assignee_id: Optional[str] = Field(default=None, index=True)  # FK to users.id
    due_date: Optional[datetime] = None
    labels: Optional[str] = None               # JSON array stored as text
    archived: bool = False
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


# ─── BoardMember ─────────────────────────────────────────────────────

class BoardMember(SQLModel, table=True):
    __tablename__ = "board_members"
    __table_args__ = (UniqueConstraint("board_id", "user_id", name="uq_board_member"),)

    id: str = Field(default_factory=ulid_field, primary_key=True)
    board_id: str = Field(index=True)
    user_id: str = Field(index=True)
    role: BoardRole = BoardRole.viewer
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ─── BoardInvite ─────────────────────────────────────────────────────

def _default_expires_at() -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=7)


def _generate_token() -> str:
    return secrets.token_urlsafe(32)


class BoardInvite(SQLModel, table=True):
    __tablename__ = "board_invites"

    id: str = Field(default_factory=ulid_field, primary_key=True)
    board_id: str = Field(index=True)
    email: str = Field(index=True)
    role: BoardRole = BoardRole.viewer
    invited_by: str = Field(index=True)
    status: InviteStatus = InviteStatus.pending
    token: str = Field(default_factory=_generate_token, unique=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = Field(default_factory=_default_expires_at)
    accepted_at: Optional[datetime] = None


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
    color: CardColor = CardColor.gray
    assignee_id: Optional[str] = None
    due_date: Optional[datetime] = None
    labels: Optional[list[str]] = None


class CardUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Priority] = None
    status: Optional[CardStatus] = None
    color: Optional[CardColor] = None
    assignee_id: Optional[str] = None
    due_date: Optional[datetime] = None
    labels: Optional[list[str]] = None


class CardRead(SQLModel):
    id: str
    column_id: str
    board_id: str
    title: str
    description: Optional[str]
    priority: Priority
    status: CardStatus
    color: CardColor
    position: int
    created_by: CreatedBy
    assignee_id: Optional[str]
    assignee_name: Optional[str] = None  # populated from User join
    due_date: Optional[datetime]
    labels: Optional[list[str]]
    archived: bool
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


# ─── Member/Invite schemas ───────────────────────────────────────────

class InviteCreate(SQLModel):
    email: EmailStr  # Security: validates email format
    role: BoardRole = BoardRole.viewer


class MemberRoleUpdate(SQLModel):
    role: BoardRole


class BoardMemberRead(SQLModel):
    id: str
    user_id: str
    user_email: str
    role: BoardRole
    created_at: datetime


class BoardInviteRead(SQLModel):
    """Invite info for API responses. Security: token excluded to prevent leakage."""
    id: str
    board_id: str
    board_name: str
    email: str
    role: BoardRole
    invited_by_email: str
    status: InviteStatus
    # Security: token removed - should only be sent via email link
    created_at: datetime
    expires_at: datetime


class MyInviteRead(SQLModel):
    """Invite info for the invited user - includes token for accept/decline."""
    id: str
    board_id: str
    board_name: str
    email: str
    role: BoardRole
    invited_by_email: str
    status: InviteStatus
    token: str  # Safe to include for the user's own invites
    created_at: datetime
    expires_at: datetime


class InviteAcceptResponse(SQLModel):
    board_id: str
    board_name: str
    role: BoardRole


class BoardReadWithRole(SQLModel):
    """Board с ролью текущего пользователя."""
    id: str
    name: str
    slug: str
    owner_id: str
    my_role: BoardRole
    created_at: datetime
