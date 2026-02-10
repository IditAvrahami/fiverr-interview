"""SQLAlchemy declarative base and optional base model."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):  # pylint: disable=too-few-public-methods
    """Declarative base for all models."""

    type_annotation_map = {datetime: DateTime(timezone=True)}


class TimestampMixin:  # pylint: disable=too-few-public-methods
    """Mixin adding id and created_at."""

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # pylint: disable=not-callable
        default=lambda: datetime.now(timezone.utc),
    )


def get_base() -> type[Base]:
    """Return the declarative base (for imports)."""
    return Base
