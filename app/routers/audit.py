from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import authenticate, Identity
from app.database import get_db
from app.schemas.audit import CalculationLogResponse

router = APIRouter()


@router.get("/calculations", response_model=list[CalculationLogResponse], summary="ดูประวัติการคำนวณย้อนหลัง")
async def list_calculations(
    hts_code: str | None = Query(default=None, description="กรองตาม HTS code"),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    identity: Identity = Depends(authenticate),
    db: AsyncSession = Depends(get_db),
):
    """แสดงรายการการคำนวณ เรียงตามเวลาล่าสุดก่อน ใช้สำหรับ audit trail

    ขอบเขตการมองเห็น:
    - ผู้ใช้ทั่วไป (role=user): เห็นเฉพาะการคำนวณของตนเอง
    - admin / service (API key, dev mode): เห็นทั้งหมด
    """
    from app.services.audit_service import AuditService

    # Regular logged-in users are scoped to their own calculations.
    # Admin and service (API key / dev-mode) callers see everything.
    scope_user_id = None
    if identity.user_id and not identity.is_admin:
        scope_user_id = identity.user_id

    service = AuditService(db)
    return await service.list_calculations(hts_code, limit, offset, user_id=scope_user_id)


@router.get("/calculations/{calculation_id}", response_model=CalculationLogResponse, summary="ดูรายละเอียดการคำนวณ")
async def get_calculation(
    calculation_id: str,
    identity: Identity = Depends(authenticate),
    db: AsyncSession = Depends(get_db),
):
    """ดึงข้อมูลการคำนวณครั้งเดียว ประกอบด้วย input, matched rules, exclusions, ผลลัพธ์

    ผู้ใช้ทั่วไปเข้าถึงได้เฉพาะการคำนวณของตนเอง (มิฉะนั้น 404);
    admin / service เข้าถึงได้ทุกรายการ
    """
    from app.services.audit_service import AuditService

    service = AuditService(db)
    log = await service.get_calculation(calculation_id)

    # Enforce ownership for regular users
    if identity.user_id and not identity.is_admin and log.user_id != identity.user_id:
        raise HTTPException(status_code=404, detail=f"Calculation '{calculation_id}' not found")

    return log
