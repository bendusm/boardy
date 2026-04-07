#!/usr/bin/env python3
"""Create demo account for Anthropic MCP Directory review.

Usage:
    docker compose exec backend python scripts/create_demo_account.py

This creates:
    - Demo user: demo@boardy.alivik.io
    - Demo board with columns and sample cards
"""

import sys
sys.path.insert(0, "/app")

from datetime import datetime, timezone
from passlib.hash import bcrypt
from sqlmodel import Session, select

from app.core.database import engine
from app.core.ulid import generate_ulid
from app.auth.models import User
from app.boards.models import Board, BoardMember, Column, Card, Comment, BoardRole, CreatedBy, CardPriority, CardStatus


DEMO_EMAIL = "demo@boardy.alivik.io"
DEMO_PASSWORD = "BoardyDemo2026!"  # Change after creating account


def create_demo_account():
    with Session(engine) as session:
        # Check if demo user exists
        existing = session.exec(
            select(User).where(User.email == DEMO_EMAIL)
        ).first()

        if existing:
            print(f"Demo user already exists: {DEMO_EMAIL}")
            return existing

        # Create demo user
        user = User(
            id=generate_ulid(),
            email=DEMO_EMAIL,
            hashed_password=bcrypt.hash(DEMO_PASSWORD),
            terms_accepted_at=datetime.now(timezone.utc),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        print(f"Created demo user: {DEMO_EMAIL}")
        return user


def create_demo_board(user_id: str):
    with Session(engine) as session:
        # Check if demo board exists
        existing = session.exec(
            select(Board).where(Board.slug == "demo-board")
        ).first()

        if existing:
            print(f"Demo board already exists: {existing.name}")
            return existing

        # Create board
        board = Board(
            id=generate_ulid(),
            name="Demo Project Board",
            slug="demo-board",
            owner_id=user_id,
        )
        session.add(board)
        session.commit()

        # Add owner membership
        member = BoardMember(
            id=generate_ulid(),
            board_id=board.id,
            user_id=user_id,
            role=BoardRole.owner,
        )
        session.add(member)

        # Create columns
        columns = [
            Column(id=generate_ulid(), board_id=board.id, name="Backlog", position=0),
            Column(id=generate_ulid(), board_id=board.id, name="To Do", position=1),
            Column(id=generate_ulid(), board_id=board.id, name="In Progress", position=2),
            Column(id=generate_ulid(), board_id=board.id, name="Review", position=3),
            Column(id=generate_ulid(), board_id=board.id, name="Done", position=4),
        ]
        for col in columns:
            session.add(col)
        session.commit()

        # Create sample cards
        cards_data = [
            # Backlog
            {"column": 0, "title": "Research competitor features", "priority": CardPriority.low, "created_by": CreatedBy.user},
            {"column": 0, "title": "Plan Q2 roadmap", "priority": CardPriority.medium, "created_by": CreatedBy.user},

            # To Do
            {"column": 1, "title": "Implement dark mode", "priority": CardPriority.medium, "created_by": CreatedBy.user,
             "description": "Add dark mode toggle to settings page"},
            {"column": 1, "title": "Fix login bug on Safari", "priority": CardPriority.high, "created_by": CreatedBy.claude},

            # In Progress
            {"column": 2, "title": "Update API documentation", "priority": CardPriority.medium, "created_by": CreatedBy.claude,
             "description": "Document new endpoints from PR #42"},
            {"column": 2, "title": "Refactor auth middleware", "priority": CardPriority.high, "created_by": CreatedBy.user},

            # Review
            {"column": 3, "title": "Add unit tests for board service", "priority": CardPriority.medium, "created_by": CreatedBy.user},

            # Done
            {"column": 4, "title": "Setup CI/CD pipeline", "priority": CardPriority.high, "created_by": CreatedBy.user, "status": CardStatus.done},
            {"column": 4, "title": "Configure Cloudflare CDN", "priority": CardPriority.medium, "created_by": CreatedBy.claude, "status": CardStatus.done},
        ]

        for i, card_data in enumerate(cards_data):
            col_idx = card_data.pop("column")
            card = Card(
                id=generate_ulid(),
                board_id=board.id,
                column_id=columns[col_idx].id,
                position=i,
                **card_data,
            )
            session.add(card)

        session.commit()
        session.refresh(board)
        print(f"Created demo board: {board.name} with {len(cards_data)} cards")
        return board


def main():
    print("=" * 50)
    print("Creating Boardy Demo Account for Anthropic Review")
    print("=" * 50)

    user = create_demo_account()
    board = create_demo_board(user.id)

    print()
    print("=" * 50)
    print("DEMO ACCOUNT CREDENTIALS")
    print("=" * 50)
    print(f"Email:    {DEMO_EMAIL}")
    print(f"Password: {DEMO_PASSWORD}")
    print(f"Board:    {board.name}")
    print()
    print("Share these credentials with Anthropic review team.")
    print("=" * 50)


if __name__ == "__main__":
    main()
