"""
Auth routes — OAuth login/callback, token refresh, user profile.

Endpoints:
- GET /auth/login/google → redirect to Google
- GET /auth/login/github → redirect to GitHub
- GET /auth/callback/google → handle callback, issue JWT
- GET /auth/callback/github → handle callback, issue JWT
- POST /auth/refresh → refresh access token
- GET /auth/me → get current user profile
- POST /auth/logout → (client-side: discard tokens)
"""

from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.oauth_service import OAuthService, OAuthError
from app.services.token_service import verify_refresh_token, create_access_token, verify_access_token
from app.config import get_settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _frontend_base(settings) -> str:
    """Resolve the frontend base URL for post-OAuth redirects."""
    return settings.frontend_url or "http://localhost:3000"


def _error_redirect(settings, provider: str, message: str) -> RedirectResponse:
    """Redirect back to the frontend login page with a readable error message.

    The frontend can read ?error=... and ?provider=... to show the user what
    went wrong instead of a raw 400/JSON blob.
    """
    query = urlencode({"error": message, "provider": provider})
    return RedirectResponse(url=f"{_frontend_base(settings)}/login?{query}")


def _get_base_url(request: Request) -> str:
    """Get the base URL from the request for redirect URIs."""
    settings = get_settings()
    if settings.frontend_url:
        return settings.frontend_url
    return str(request.base_url).rstrip("/")


# =============================================================================
# Google OAuth
# =============================================================================

@router.get("/login/google", summary="เริ่ม Google OAuth login")
async def login_google(request: Request):
    """Redirect user to Google OAuth consent screen."""
    settings = get_settings()
    redirect_uri = f"{settings.backend_url}/auth/callback/google"
    service = OAuthService.__new__(OAuthService)
    service.settings = settings
    auth_url = service.get_google_auth_url(redirect_uri)
    return RedirectResponse(url=auth_url)


@router.get("/callback/google", summary="Google OAuth callback")
async def callback_google(
    code: str | None = Query(None),
    error: str | None = Query(None),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Handle Google OAuth callback — exchange code, create user, return tokens.

    On any failure (provider error, missing code, or network/DNS issue) we
    redirect the user back to the frontend login page with a readable message
    instead of surfacing a raw 400.
    """
    settings = get_settings()

    # Provider returned an error (e.g. user denied consent)
    if error:
        return _error_redirect(settings, "google", f"Google sign-in was cancelled or failed: {error}")

    # Provider returned no authorization code
    if not code:
        return _error_redirect(
            settings,
            "google",
            "Google did not return an authorization code. Please try signing in again.",
        )

    redirect_uri = f"{settings.backend_url}/auth/callback/google"

    try:
        service = OAuthService(db)
        result = await service.handle_google_callback(code, redirect_uri)
    except OAuthError as e:
        return _error_redirect(settings, "google", str(e))
    except Exception as e:  # noqa: BLE001 — unknown failure, still return something usable
        return _error_redirect(settings, "google", f"Unexpected error during Google sign-in: {type(e).__name__}")

    # Redirect to frontend with tokens
    frontend_url = _frontend_base(settings)
    return RedirectResponse(
        url=f"{frontend_url}/auth/success?access_token={result['access_token']}&refresh_token={result['refresh_token']}"
    )


# =============================================================================
# GitHub OAuth
# =============================================================================

@router.get("/login/github", summary="เริ่ม GitHub OAuth login")
async def login_github(request: Request):
    """Redirect user to GitHub OAuth consent screen."""
    settings = get_settings()
    redirect_uri = f"{settings.backend_url}/auth/callback/github"
    service = OAuthService.__new__(OAuthService)
    service.settings = settings
    auth_url = service.get_github_auth_url(redirect_uri)
    return RedirectResponse(url=auth_url)


@router.get("/callback/github", summary="GitHub OAuth callback")
async def callback_github(
    code: str | None = Query(None),
    error: str | None = Query(None),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Handle GitHub OAuth callback — exchange code, create user, return tokens."""
    settings = get_settings()

    if error:
        return _error_redirect(settings, "github", f"GitHub sign-in was cancelled or failed: {error}")

    if not code:
        return _error_redirect(
            settings,
            "github",
            "GitHub did not return an authorization code. Please try signing in again.",
        )

    redirect_uri = f"{settings.backend_url}/auth/callback/github"

    try:
        service = OAuthService(db)
        result = await service.handle_github_callback(code, redirect_uri)
    except OAuthError as e:
        return _error_redirect(settings, "github", str(e))
    except Exception as e:  # noqa: BLE001
        return _error_redirect(settings, "github", f"Unexpected error during GitHub sign-in: {type(e).__name__}")

    frontend_url = _frontend_base(settings)
    return RedirectResponse(
        url=f"{frontend_url}/auth/success?access_token={result['access_token']}&refresh_token={result['refresh_token']}"
    )


# =============================================================================
# Token Management
# =============================================================================

class RefreshRequest(BaseModel):
    """Request body for the token refresh endpoint.

    The frontend sends `{"refresh_token": "..."}` as JSON, so we accept a body
    model rather than a query parameter.
    """

    refresh_token: str


@router.post("/refresh", summary="Refresh access token")
async def refresh_token(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Exchange a valid refresh token for a new access token."""
    payload = verify_refresh_token(body.refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user_id = payload["sub"]

    # Fetch user to get current role
    from sqlalchemy import select
    from app.models.user import User
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    new_access_token = create_access_token(user.id, user.role)
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.get("/me", summary="ดูโปรไฟล์ผู้ใช้ปัจจุบัน")
async def get_me(request: Request, db: AsyncSession = Depends(get_db)):
    """Get the currently authenticated user's profile."""
    from app.auth import get_current_user
    user = await get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "avatar_url": user.avatar_url,
        "role": user.role,
        "created_at": str(user.created_at),
    }


@router.post("/logout", summary="Logout (client discards tokens)")
async def logout():
    """
    Logout — stateless JWT means no server-side invalidation needed.
    Client should discard tokens. This endpoint exists for API completeness.
    """
    return {"message": "Logged out successfully. Discard your tokens."}
