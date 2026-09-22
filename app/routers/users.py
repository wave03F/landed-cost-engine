"""
User management routes (admin only).

Endpoints:
- GET  /users              → list all users
- GET  /users/{user_id}    → get a single user
- PUT  /users/{user_id}/role → change a user's role (promote/demote admin)
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_admin, Identity
from app.database import get_db
from app.schemas.user import UserResponse, UserRoleUpdate
from app.services.user_service import UserService

router = APIRouter(tags=["User Management"])


@router.get(
    "/users",
    response_model=list[UserResponse],
    summary="ดูรายชื่อผู้ใช้ทั้งหมด (admin)",
)
async def list_users(
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    _: Identity = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """แสดงรายชื่อผู้ใช้ทั้งหมด เรียงตามวันที่สร้างล่าสุดก่อน (ต้องเป็น admin)"""
    service = UserService(db)
    return await service.list_users(limit, offset)


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="ดูข้อมูลผู้ใช้รายคน (admin)",
)
async def get_user(
    user_id: str,
    _: Identity = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """ดึงข้อมูลผู้ใช้รายคน คืน 404 ถ้าไม่พบ (ต้องเป็น admin)"""
    service = UserService(db)
    return await service.get_user(user_id)


@router.put(
    "/users/{user_id}/role",
    response_model=UserResponse,
    summary="เปลี่ยน role ผู้ใช้ (admin)",
)
async def update_user_role(
    user_id: str,
    data: UserRoleUpdate,
    identity: Identity = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """เลื่อน/ลดสิทธิ์ผู้ใช้ระหว่าง 'user' และ 'admin' (ต้องเป็น admin).

    ป้องกันไม่ให้ admin ลดสิทธิ์ของบัญชีตัวเอง (กันระบบล็อกตัวเองออกจาก admin คนสุดท้าย).
    """
    service = UserService(db)
    return await service.update_role(user_id, data.role, acting_user_id=identity.user_id)
