"""
User Favorites — Save/bookmark HTS codes for quick access.
Requires JWT authentication (user must be logged in).
"""

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.token_service import verify_access_token
from app.models.user import UserFavorite

router = APIRouter(tags=["Favorites"])
_bearer = HTTPBearer(auto_error=False)


class FavoriteCreate(BaseModel):
    hts_code: str = Field(..., description="HTS code to save")
    note: str | None = Field(default=None, description="Optional note")


class FavoriteResponse(BaseModel):
    id: str
    hts_code: str
    note: str | None
    created_at: str

    model_config = {"from_attributes": True}


async def _get_user_id(credentials: HTTPAuthorizationCredentials | None = Security(_bearer)) -> str:
    if not credentials:
        raise HTTPException(status_code=401, detail="Login required to use favorites")
    payload = verify_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload["sub"]


@router.get("/favorites", response_model=list[FavoriteResponse], summary="ดู HTS codes ที่บันทึกไว้")
async def list_favorites(
    user_id: str = Depends(_get_user_id),
    db: AsyncSession = Depends(get_db),
):
    """List all saved HTS codes for the current user."""
    stmt = select(UserFavorite).where(UserFavorite.user_id == user_id).order_by(UserFavorite.created_at.desc())
    result = await db.execute(stmt)
    favorites = result.scalars().all()
    return [
        FavoriteResponse(
            id=f.id,
            hts_code=f.hts_code,
            note=f.note,
            created_at=str(f.created_at),
        )
        for f in favorites
    ]


@router.post("/favorites", response_model=FavoriteResponse, status_code=201, summary="บันทึก HTS code")
async def add_favorite(
    data: FavoriteCreate,
    user_id: str = Depends(_get_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Save an HTS code as a favorite."""
    # Check if already saved
    stmt = select(UserFavorite).where(
        UserFavorite.user_id == user_id,
        UserFavorite.hts_code == data.hts_code,
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="HTS code already in favorites")

    fav = UserFavorite(user_id=user_id, hts_code=data.hts_code, note=data.note)
    db.add(fav)
    await db.flush()
    return FavoriteResponse(id=fav.id, hts_code=fav.hts_code, note=fav.note, created_at=str(fav.created_at))


@router.delete("/favorites/{favorite_id}", status_code=204, summary="ลบ HTS code ที่บันทึกไว้")
async def remove_favorite(
    favorite_id: str,
    user_id: str = Depends(_get_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Remove a saved HTS code."""
    stmt = select(UserFavorite).where(
        UserFavorite.id == favorite_id,
        UserFavorite.user_id == user_id,
    )
    result = await db.execute(stmt)
    fav = result.scalar_one_or_none()
    if not fav:
        raise HTTPException(status_code=404, detail="Favorite not found")
    await db.delete(fav)
    await db.flush()
