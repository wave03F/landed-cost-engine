"""
OAuth Service — Handles OAuth flow for Google and GitHub.

Flow:
1. Generate authorization URL (redirect user to provider)
2. Exchange code for token (provider callback)
3. Fetch user info from provider
4. Create or update user in database
5. Issue JWT tokens
"""

from datetime import datetime, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.user import User
from app.services.token_service import create_access_token, create_refresh_token


class OAuthService:
    """Handles OAuth login for Google and GitHub."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()

    # =========================================================================
    # Google OAuth
    # =========================================================================

    def get_google_auth_url(self, redirect_uri: str) -> str:
        """Generate Google OAuth authorization URL."""
        params = {
            "client_id": self.settings.google_client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"https://accounts.google.com/o/oauth2/v2/auth?{query}"

    async def handle_google_callback(self, code: str, redirect_uri: str) -> dict:
        """Exchange Google code for tokens, fetch user info, create/update user."""
        # Exchange code for token
        async with httpx.AsyncClient() as client:
            token_resp = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": self.settings.google_client_id,
                    "client_secret": self.settings.google_client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            token_data = token_resp.json()

            if "access_token" not in token_data:
                raise ValueError(f"Google token exchange failed: {token_data}")

            # Fetch user info
            user_resp = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {token_data['access_token']}"},
            )
            user_info = user_resp.json()

        # Create or update user
        user = await self._upsert_user(
            email=user_info["email"],
            name=user_info.get("name", user_info["email"]),
            avatar_url=user_info.get("picture"),
            oauth_provider="google",
            oauth_id=user_info["id"],
        )

        # Issue JWT tokens
        access_token = create_access_token(user.id, user.role)
        refresh_token = create_refresh_token(user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "avatar_url": user.avatar_url,
                "role": user.role,
            },
        }

    # =========================================================================
    # GitHub OAuth
    # =========================================================================

    def get_github_auth_url(self, redirect_uri: str) -> str:
        """Generate GitHub OAuth authorization URL."""
        params = {
            "client_id": self.settings.github_client_id,
            "redirect_uri": redirect_uri,
            "scope": "read:user user:email",
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"https://github.com/login/oauth/authorize?{query}"

    async def handle_github_callback(self, code: str, redirect_uri: str) -> dict:
        """Exchange GitHub code for tokens, fetch user info, create/update user."""
        async with httpx.AsyncClient() as client:
            # Exchange code for token
            token_resp = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "code": code,
                    "client_id": self.settings.github_client_id,
                    "client_secret": self.settings.github_client_secret,
                    "redirect_uri": redirect_uri,
                },
                headers={"Accept": "application/json"},
            )
            token_data = token_resp.json()

            if "access_token" not in token_data:
                raise ValueError(f"GitHub token exchange failed: {token_data}")

            # Fetch user info
            user_resp = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {token_data['access_token']}"},
            )
            user_info = user_resp.json()

            # Fetch email (might be private)
            email = user_info.get("email")
            if not email:
                email_resp = await client.get(
                    "https://api.github.com/user/emails",
                    headers={"Authorization": f"Bearer {token_data['access_token']}"},
                )
                emails = email_resp.json()
                primary = next((e for e in emails if e.get("primary")), emails[0] if emails else None)
                email = primary["email"] if primary else f"{user_info['login']}@github.local"

        # Create or update user
        user = await self._upsert_user(
            email=email,
            name=user_info.get("name") or user_info["login"],
            avatar_url=user_info.get("avatar_url"),
            oauth_provider="github",
            oauth_id=str(user_info["id"]),
        )

        # Issue JWT tokens
        access_token = create_access_token(user.id, user.role)
        refresh_token = create_refresh_token(user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "avatar_url": user.avatar_url,
                "role": user.role,
            },
        }

    # =========================================================================
    # User management
    # =========================================================================

    async def _upsert_user(
        self,
        email: str,
        name: str,
        avatar_url: str | None,
        oauth_provider: str,
        oauth_id: str,
    ) -> User:
        """Create user if not exists, or update last login."""
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            # Update existing user
            user.last_login_at = datetime.now(timezone.utc)
            user.avatar_url = avatar_url or user.avatar_url
            user.name = name or user.name
        else:
            # Create new user
            user = User(
                email=email,
                name=name,
                avatar_url=avatar_url,
                oauth_provider=oauth_provider,
                oauth_id=oauth_id,
                role="user",
                last_login_at=datetime.now(timezone.utc),
            )
            self.db.add(user)

        await self.db.flush()
        return user
