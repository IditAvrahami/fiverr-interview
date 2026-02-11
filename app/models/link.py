"""Link model for URL shortener."""

from typing import List, Optional
from datetime import datetime, UTC
from sqlalchemy import String, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Link(Base, TimestampMixin):
    """URL shortening link model."""

    __tablename__ = "links"

    original_url: Mapped[str] = mapped_column(String, nullable=False, index=True)
    short_code: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)

    # Relationship to Click model
    clicks: Mapped[List["Click"]] = relationship(
        "Click", back_populates="link", cascade="all, delete-orphan"
    )


class Click(Base, TimestampMixin):
    """Click tracking model."""

    __tablename__ = "clicks"

    link_id: Mapped[int] = mapped_column(ForeignKey("links.id"), nullable=False, index=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationship to Link model
    link: Mapped["Link"] = relationship("Link", back_populates="clicks")