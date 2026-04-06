from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.database import get_session
from app.core.deps import get_current_user
from app.auth.models import User
from .models import (
    BoardCreate, BoardRead,
    ColumnCreate, ColumnRead,
    CardCreate, CardUpdate, CardRead, CardMove,
    CommentCreate, CommentRead,
)
from . import service

router = APIRouter()


def _check_board(session, board_id, user):
    board = service.get_board(session, board_id, user.id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board


def _check_card(session, card_id):
    card = service.get_card(session, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card


# ─── Boards ──────────────────────────────────────────────────────────

@router.get("/boards", response_model=list[BoardRead])
def list_boards(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return service.get_boards(session, current_user.id)


@router.post("/boards", response_model=BoardRead, status_code=status.HTTP_201_CREATED)
def create_board(
    body: BoardCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return service.create_board(session, owner_id=current_user.id, name=body.name)


@router.get("/boards/{board_id}")
def get_board(
    board_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    board = _check_board(session, board_id, current_user)
    return service.get_board_full(session, board.id)


@router.delete("/boards/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_board(
    board_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    board = _check_board(session, board_id, current_user)
    service.delete_board(session, board)


# ─── Columns ─────────────────────────────────────────────────────────

@router.get("/boards/{board_id}/columns", response_model=list[ColumnRead])
def list_columns(
    board_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    _check_board(session, board_id, current_user)
    return service.get_columns(session, board_id)


@router.post("/boards/{board_id}/columns", response_model=ColumnRead, status_code=201)
def create_column(
    board_id: str,
    body: ColumnCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    _check_board(session, board_id, current_user)
    return service.create_column(session, board_id, body.name, body.position)


# ─── Cards ───────────────────────────────────────────────────────────

@router.get("/boards/{board_id}/columns/{column_id}/cards", response_model=list[CardRead])
def list_cards(
    board_id: str,
    column_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    _check_board(session, board_id, current_user)
    return service.get_cards(session, column_id)


@router.post("/boards/{board_id}/columns/{column_id}/cards", response_model=CardRead, status_code=201)
def create_card(
    board_id: str,
    column_id: str,
    body: CardCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    _check_board(session, board_id, current_user)
    return service.create_card(
        session,
        board_id=board_id,
        column_id=column_id,
        title=body.title,
        description=body.description,
        priority=body.priority,
    )


@router.patch("/cards/{card_id}", response_model=CardRead)
def update_card(
    card_id: str,
    body: CardUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    card = _check_card(session, card_id)
    _check_board(session, card.board_id, current_user)
    return service.update_card(
        session, card,
        title=body.title,
        description=body.description,
        priority=body.priority,
        status=body.status,
    )


@router.post("/cards/{card_id}/move", response_model=CardRead)
def move_card(
    card_id: str,
    body: CardMove,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    card = _check_card(session, card_id)
    _check_board(session, card.board_id, current_user)
    return service.move_card(session, card, body.to_column_id, body.position)


@router.delete("/cards/{card_id}", status_code=204)
def delete_card(
    card_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    card = _check_card(session, card_id)
    _check_board(session, card.board_id, current_user)
    session.delete(card)
    session.commit()


# ─── Comments ────────────────────────────────────────────────────────

@router.get("/cards/{card_id}/comments", response_model=list[CommentRead])
def list_comments(
    card_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    card = _check_card(session, card_id)
    _check_board(session, card.board_id, current_user)
    return service.get_comments(session, card_id)


@router.post("/cards/{card_id}/comments", response_model=CommentRead, status_code=201)
def add_comment(
    card_id: str,
    body: CommentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    card = _check_card(session, card_id)
    _check_board(session, card.board_id, current_user)
    return service.add_comment(session, card_id, body.text)
