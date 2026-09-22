"""
User management service — admin-facing operations.

Provides listing users and changing a user's role (promote/demote admin).
"""

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


VALID_ROLES = {"user", "admin"}


class UserService:
    """Service for managing user accounts (admin operations)."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_users(self, limit: int, offset: int) -> list[User]:
        """List all users, newest first."""
        stmt = (
            select(User)
            .order_by(User.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_user(self, user_id: str) -> User:
        """Get a single user by id. Raises 404 if not found."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")
        return user

    async def update_role(
        self, user_id: str, new_role: str, acting_user_id: str | None
    ) -> User:
        """Change a user's role. Raises 404 if not found, 400 for invalid role.

        Guards against an admin demoting themselves, which could lock the system
        out of its last administrator.
        """
        if new_role not in VALID_ROLES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid role '{new_role}'. Must be one of: {sorted(VALID_ROLES)}",
            )

        user = await self.get_user(user_id)

        # Prevent an admin from demoting their own account.
        if (
            acting_user_id is not None
            and acting_user_id == user_id
            and user.role == "admin"
            and new_role != "admin"
        ):
            raise HTTPException(
                status_code=400,
                detail="You cannot remove your own admin role.",
            )

        user.role = new_role
        await self.db.flush()
        return user
