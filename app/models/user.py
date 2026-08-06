"""
User model for OAuth authentication.

Stores user identity from OAuth providers (Google, GitHub).
No password field — authentication is delegated to providers.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    """
    User account linked to an OAuth provider.

    Roles:
    - user: can calculate, view own history, save favorites
    - admin: full CRUD on tariff rules, exclusions, FX rates, HTS codes
    """

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    oauth_provider: Mapped[str] = mapped_column(String(20), nullable=False)  # "google" or "github"
    oauth_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user")  # "user" or "admin"
    daily_calculations: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_calculation_date: Mapped[str | None] = mapped_column(String(10), nullable=True)  # "YYYY-MM-DD"
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class UserFavorite(Base):
    """
    Saved/bookmarked HTS codes for a user.
    """

    __tablename__ = "user_favorites"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    hts_code: Mapped[str] = mapped_column(String(20), nullable=False)
    note: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
