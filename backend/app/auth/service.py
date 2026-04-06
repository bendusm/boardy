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


def create_user(session: Session, email: str, password: str) -> User:
    user = User(email=email, hashed_password=hash_password(password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def authenticate_user(session: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(session, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
