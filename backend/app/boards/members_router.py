from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.database import get_session
from app.core.deps import get_current_user
from app.auth.models import User
from .models import (
    BoardRole, InviteCreate, MemberRoleUpdate,
    BoardMemberRead, BoardInviteRead, MyInviteRead, InviteAcceptResponse,
)
from . import service

router = APIRouter()


# ─── Board Members ───────────────────────────────────────────────────

# Virtual AI agent ID - used for assigning tasks to AI
AI_AGENT_ID = "ai-agent"


@router.get("/boards/{board_id}/members", response_model=list[BoardMemberRead])
def list_members(
    board_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """List all members of a board including owner and AI agent. Any member can view."""
    board = service.check_board_access(session, board_id, current_user.id, BoardRole.viewer)

    result = []

    # Add owner first
    owner = session.get(User, board.owner_id)
    if owner:
        result.append(BoardMemberRead(
            id=f"owner-{board.owner_id}",  # Virtual ID for owner
            user_id=board.owner_id,
            user_email=owner.email,
            role=BoardRole.owner,
            created_at=board.created_at,
        ))

    # Add AI agent as virtual member
    result.append(BoardMemberRead(
        id=AI_AGENT_ID,
        user_id=AI_AGENT_ID,
        user_email="AI Assistant",
        role=BoardRole.editor,  # AI has editor permissions
        created_at=board.created_at,
    ))

    # Add other members
    members = service.get_board_members(session, board_id)
    for member, email in members:
        # Skip if this is the owner (already added)
        if member.user_id == board.owner_id:
            continue
        result.append(BoardMemberRead(
            id=member.id,
            user_id=member.user_id,
            user_email=email,
            role=member.role,
            created_at=member.created_at,
        ))

    return result


@router.patch("/boards/{board_id}/members/{member_id}", response_model=BoardMemberRead)
def update_member_role(
    board_id: str,
    member_id: str,
    body: MemberRoleUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Change member's role. Owner only."""
    service.check_board_access(session, board_id, current_user.id, BoardRole.owner)

    member = service.get_member_by_id(session, member_id)
    if not member or member.board_id != board_id:
        raise HTTPException(status_code=404, detail="Member not found")

    if member.role == BoardRole.owner:
        raise HTTPException(status_code=400, detail="Cannot change owner's role")

    updated = service.update_member_role(session, member, body.role)
    user = session.get(User, updated.user_id)
    return BoardMemberRead(
        id=updated.id,
        user_id=updated.user_id,
        user_email=user.email if user else "",
        role=updated.role,
        created_at=updated.created_at,
    )


@router.delete("/boards/{board_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    board_id: str,
    member_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Remove a member from board. Owner only."""
    service.check_board_access(session, board_id, current_user.id, BoardRole.owner)

    member = service.get_member_by_id(session, member_id)
    if not member or member.board_id != board_id:
        raise HTTPException(status_code=404, detail="Member not found")

    if member.role == BoardRole.owner:
        raise HTTPException(status_code=400, detail="Cannot remove owner")

    service.remove_board_member(session, member)


# ─── Board Invites ───────────────────────────────────────────────────

@router.post("/boards/{board_id}/invites", response_model=BoardInviteRead, status_code=status.HTTP_201_CREATED)
def create_invite(
    board_id: str,
    body: InviteCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Invite a user to the board. Owner only."""
    board = service.check_board_access(session, board_id, current_user.id, BoardRole.owner)

    email = body.email.lower()

    # Cannot invite yourself
    if email == current_user.email.lower():
        raise HTTPException(status_code=400, detail="Cannot invite yourself")

    # Check if already a member
    if service.check_existing_member_by_email(session, board_id, email):
        raise HTTPException(status_code=400, detail="User is already a member")

    # Check for existing pending invite
    if service.check_existing_invite(session, board_id, email):
        raise HTTPException(status_code=400, detail="Pending invite already exists")

    # Cannot assign owner role via invite
    if body.role == BoardRole.owner:
        raise HTTPException(status_code=400, detail="Cannot invite as owner")

    invite = service.create_invite(session, board_id, email, body.role, current_user.id)

    # Note: token is intentionally excluded from response for security
    # It should only be sent via email to the invited user
    return BoardInviteRead(
        id=invite.id,
        board_id=invite.board_id,
        board_name=board.name,
        email=invite.email,
        role=invite.role,
        invited_by_email=current_user.email,
        status=invite.status,
        created_at=invite.created_at,
        expires_at=invite.expires_at,
    )


@router.get("/boards/{board_id}/invites", response_model=list[BoardInviteRead])
def list_invites(
    board_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """List pending invites for a board. Owner only."""
    board = service.check_board_access(session, board_id, current_user.id, BoardRole.owner)

    invites = service.get_pending_invites(session, board_id)
    return [
        BoardInviteRead(
            id=inv.id,
            board_id=inv.board_id,
            board_name=board.name,
            email=inv.email,
            role=inv.role,
            invited_by_email=current_user.email,
            status=inv.status,
            created_at=inv.created_at,
            expires_at=inv.expires_at,
        )
        for inv in invites
    ]


@router.delete("/boards/{board_id}/invites/{invite_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_invite(
    board_id: str,
    invite_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Cancel a pending invite. Owner only."""
    service.check_board_access(session, board_id, current_user.id, BoardRole.owner)

    invite = service.get_invite_by_id(session, invite_id)
    if not invite or invite.board_id != board_id:
        raise HTTPException(status_code=404, detail="Invite not found")

    service.cancel_invite(session, invite)


# ─── My Invites (for invited users) ──────────────────────────────────

@router.get("/invites/my", response_model=list[MyInviteRead])
def my_invites(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get all pending invites for current user. Includes token for accept/decline."""
    invites = service.get_user_pending_invites(session, current_user.email)
    return [
        MyInviteRead(
            id=inv.id,
            board_id=inv.board_id,
            board_name=board_name,
            email=inv.email,
            role=inv.role,
            invited_by_email=inviter_email,
            status=inv.status,
            token=inv.token,  # Safe: this is the user's own invite
            created_at=inv.created_at,
            expires_at=inv.expires_at,
        )
        for inv, board_name, inviter_email in invites
    ]


@router.post("/invites/{token}/accept", response_model=InviteAcceptResponse)
def accept_invite(
    token: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Accept an invite by token."""
    invite = service.get_invite_by_token(session, token)
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")

    # Check email matches
    if invite.email.lower() != current_user.email.lower():
        raise HTTPException(status_code=403, detail="This invite is for a different email")

    # Check not expired (handle timezone-naive datetime from DB)
    expires_at = invite.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invite has expired")

    # Check still pending
    if invite.status.value != "pending":
        raise HTTPException(status_code=400, detail="Invite is no longer valid")

    # Accept and create membership
    service.accept_invite(session, invite, current_user.id)

    board = session.get(service.Board, invite.board_id)
    return InviteAcceptResponse(
        board_id=invite.board_id,
        board_name=board.name if board else "",
        role=invite.role,
    )


@router.post("/invites/{token}/decline", status_code=status.HTTP_204_NO_CONTENT)
def decline_invite(
    token: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Decline an invite by token."""
    invite = service.get_invite_by_token(session, token)
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")

    # Check email matches
    if invite.email.lower() != current_user.email.lower():
        raise HTTPException(status_code=403, detail="This invite is for a different email")

    service.decline_invite(session, invite)
