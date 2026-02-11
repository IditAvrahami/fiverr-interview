"""SQLAlchemy models. Add new models here."""

from app.db.base import Base
from app.models.link import Link, Click

__all__ = ["Base", "Link", "Click"]
