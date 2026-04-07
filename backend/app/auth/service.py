from datetime import datetime, timedelta, timezone
from typing import Optional
import secrets

from jose import jwt
from passlib.context import CryptContext
from sqlmodel import Session, select

from app.core.config import settings
from .models import User, TokenBlacklist

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    # Security: Add unique jti (JWT ID) for token revocation support
    jti = secrets.token_urlsafe(16)
    payload = {"sub": user_id, "exp": expire, "type": "access", "jti": jti}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def blacklist_token(session: Session, token: str, user_id: str) -> None:
    """Add a token to the blacklist for logout invalidation.

    Security: Blacklisted tokens are rejected until they would have expired naturally.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        jti = payload.get("jti")
        exp = payload.get("exp")

        if not jti:
            return  # Old tokens without jti can't be blacklisted

        expires_at = datetime.fromtimestamp(exp, tz=timezone.utc) if exp else datetime.now(timezone.utc)

        # Check if already blacklisted
        existing = session.exec(
            select(TokenBlacklist).where(TokenBlacklist.token_jti == jti)
        ).first()
        if existing:
            return

        blacklist_entry = TokenBlacklist(
            token_jti=jti,
            user_id=user_id,
            expires_at=expires_at,
        )
        session.add(blacklist_entry)
        session.commit()
    except Exception:
        pass  # Invalid token - nothing to blacklist


def is_token_blacklisted(session: Session, jti: str) -> bool:
    """Check if a token's jti is in the blacklist."""
    entry = session.exec(
        select(TokenBlacklist).where(TokenBlacklist.token_jti == jti)
    ).first()
    return entry is not None


def cleanup_expired_blacklist(session: Session) -> int:
    """Remove expired entries from the blacklist. Returns count of removed entries."""
    now = datetime.now(timezone.utc)
    expired = session.exec(
        select(TokenBlacklist).where(TokenBlacklist.expires_at < now)
    ).all()
    count = len(expired)
    for entry in expired:
        session.delete(entry)
    session.commit()
    return count


def get_user_by_email(session: Session, email: str) -> Optional[User]:
    return session.exec(select(User).where(User.email == email)).first()


def create_user(session: Session, email: str, password: str, record_terms_consent: bool = False) -> User:
    user = User(
        email=email,
        hashed_password=hash_password(password),
        terms_accepted_at=datetime.now(timezone.utc) if record_terms_consent else None,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def authenticate_user(session: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(session, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def delete_user_account(session: Session, user_id: str) -> None:
    """Delete user account and all associated data.

    This deletes:
    - All boards owned by the user (cascades to columns, cards, comments, attachments)
    - All board memberships
    - All pending invites (sent and received)
    - All OAuth tokens
    - All blacklisted tokens
    - The user record itself
    """
    from app.boards.models import Board, BoardMember, BoardInvite, Card, Column, Comment, Attachment
    from .models import OAuthToken, OAuthAuthCode

    # Delete all boards owned by user (will cascade to columns, cards, etc.)
    owned_boards = session.exec(select(Board).where(Board.owner_id == user_id)).all()
    for board in owned_boards:
        # Delete all columns and their cards
        columns = session.exec(select(Column).where(Column.board_id == board.id)).all()
        for col in columns:
            # Delete cards and their comments/attachments
            cards = session.exec(select(Card).where(Card.column_id == col.id)).all()
            for card in cards:
                session.exec(select(Comment).where(Comment.card_id == card.id)).all()
                for comment in session.exec(select(Comment).where(Comment.card_id == card.id)).all():
                    session.delete(comment)
                for attachment in session.exec(select(Attachment).where(Attachment.card_id == card.id)).all():
                    session.delete(attachment)
                session.delete(card)
            session.delete(col)
        # Delete board members
        for member in session.exec(select(BoardMember).where(BoardMember.board_id == board.id)).all():
            session.delete(member)
        # Delete board invites
        for invite in session.exec(select(BoardInvite).where(BoardInvite.board_id == board.id)).all():
            session.delete(invite)
        session.delete(board)

    # Remove user from boards they're a member of (but don't own)
    for member in session.exec(select(BoardMember).where(BoardMember.user_id == user_id)).all():
        session.delete(member)

    # Delete pending invites sent to this user's email
    user = session.get(User, user_id)
    if user:
        for invite in session.exec(select(BoardInvite).where(BoardInvite.email == user.email)).all():
            session.delete(invite)

    # Delete OAuth tokens
    for token in session.exec(select(OAuthToken).where(OAuthToken.user_id == user_id)).all():
        session.delete(token)

    # Delete OAuth auth codes
    for code in session.exec(select(OAuthAuthCode).where(OAuthAuthCode.user_id == user_id)).all():
        session.delete(code)

    # Delete blacklisted tokens
    for entry in session.exec(select(TokenBlacklist).where(TokenBlacklist.user_id == user_id)).all():
        session.delete(entry)

    # Finally, delete the user
    if user:
        session.delete(user)

    session.commit()
