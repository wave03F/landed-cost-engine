"""
Authentication module — supports both JWT Bearer tokens and API Key.

Priority:
1. JWT Bearer token (Authorization: Bearer <token>) → authenticated user
2. API Key (X-API-Key header) → anonymous/service access
3. No auth + no keys configured → dev mode (allow all)

Role-based access:
- require_user: any authenticated user
- require_admin: only role="admin"
"""

from fastapi import Security, HTTPException, status, Request, Depends
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.services.token_service import verify_access_token
from app.database import get_db
from app.models.user import User

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(request: Request, db: AsyncSession) -> User | None:
    """
    Extract user from JWT token if present.
    Returns User object or None.
    """
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        payload = verify_access_token(token)
        if payload:
            user_id = payload.get("sub")
            result = await db.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()
    return None


async def require_api_key(
    api_key: str | None = Security(_api_key_header),
    credentials: HTTPAuthorizationCredentials | None = Security(_bearer_scheme),
) -> str:
    """
    Dependency that validates authentication.
    Accepts either JWT Bearer token OR API Key.
    Returns user_id (from JWT) or "api-key" or "dev-mode".
    """
    settings = get_settings()

    # Try JWT first
    if credentials and credentials.credentials:
        payload = verify_access_token(credentials.credentials)
        if payload:
            return payload["sub"]  # user_id
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )

    # Try API Key
    if api_key:
        if not settings.api_keys:
            return "api-key-dev"
        if api_key in settings.api_keys:
            return "api-key"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    # No auth provided
    if not settings.api_keys and not settings.jwt_secret:
        return "dev-mode"

    if not settings.api_keys:
        return "dev-mode"

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Provide a Bearer token or X-API-Key header.",
    )


async def require_admin(
    credentials: HTTPAuthorizationCredentials | None = Security(_bearer_scheme),
) -> str:
    """
    Dependency that requires admin role.
    Only JWT Bearer with role=admin passes.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin access requires a Bearer token",
        )

    payload = verify_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )

    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )

    return payload["sub"]
