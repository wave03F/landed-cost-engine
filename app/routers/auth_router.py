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

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.oauth_service import OAuthService
from app.services.token_service import verify_refresh_token, create_access_token, verify_access_token
from app.config import get_settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


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
    code: str = Query(...),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Handle Google OAuth callback — exchange code, create user, return tokens via HTML form POST."""
    settings = get_settings()
    redirect_uri = f"{settings.backend_url}/auth/callback/google"

    try:
        service = OAuthService(db)
        result = await service.handle_google_callback(code, redirect_uri)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth failed: {type(e).__name__}: {str(e)}")

    # Redirect with tokens in URL fragment (#)
    # Fragment is never sent to server, not logged, not in browser history entries
    frontend_url = settings.frontend_url or "http://localhost:3000"
    return RedirectResponse(
        url=f"{frontend_url}/auth/success#access_token={result['access_token']}&refresh_token={result['refresh_token']}"
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
    code: str = Query(...),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Handle GitHub OAuth callback — exchange code, create user, return tokens via secure form POST."""
    settings = get_settings()
    redirect_uri = f"{settings.backend_url}/auth/callback/github"

    try:
        service = OAuthService(db)
        result = await service.handle_github_callback(code, redirect_uri)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth failed: {type(e).__name__}: {str(e)}")

    frontend_url = settings.frontend_url or "http://localhost:3000"
    html = f"""
    <html><body>
    <form id="f" method="POST" action="{frontend_url}/auth/callback">
        <input type="hidden" name="access_token" value="{result['access_token']}" />
        <input type="hidden" name="refresh_token" value="{result['refresh_token']}" />
    </form>
    <script>document.getElementById('f').submit();</script>
    </body></html>
    """
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html)


# =============================================================================
# Token Management
# =============================================================================

@router.post("/refresh", summary="Refresh access token")
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """Exchange a valid refresh token for a new access token."""
    payload = verify_refresh_token(refresh_token)
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
