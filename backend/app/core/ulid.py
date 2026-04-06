"""ULID helpers — хронологически сортируемые, URL-safe ID."""
from ulid import ULID


def new_ulid() -> str:
    return str(ULID())


def ulid_field() -> str:
    """Default factory для SQLModel полей."""
    return new_ulid()
