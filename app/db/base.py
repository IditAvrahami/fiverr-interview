"""SQLAlchemy declarative base and optional base model."""

from datetime import UTC, datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base for all models."""

    type_annotation_map = {datetime: DateTime(timezone=True)}


class TimestampMixin:
    """Mixin adding id and created_at."""

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(UTC),
    )


def get_base() -> type[Base]:
    """Return the declarative base (for imports)."""
    return Base
