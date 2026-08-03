"""
API Key authentication.

Simple header-based auth using X-API-Key header.
Keys are configured via environment variable API_KEYS (comma-separated).

For production, replace with OAuth2/JWT. This is sufficient for a portfolio demo
where you want to show that auth exists without full user management.
"""

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

from app.config import get_settings

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key(api_key: str | None = Security(_api_key_header)) -> str:
    """
    Dependency that validates the API key from the X-API-Key header.
    Returns the validated key on success, raises 401 on failure.
    """
    settings = get_settings()

    if not settings.api_keys:
        # No keys configured = auth disabled (dev mode)
        return "dev-mode"

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Provide it via the X-API-Key header.",
        )

    if api_key not in settings.api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )

    return api_key
