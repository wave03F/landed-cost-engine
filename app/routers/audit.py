from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_api_key
from app.database import get_db
from app.schemas.audit import CalculationLogResponse

router = APIRouter(dependencies=[Depends(require_api_key)])


@router.get("/calculations", response_model=list[CalculationLogResponse], summary="ดูประวัติการคำนวณย้อนหลัง")
async def list_calculations(
    hts_code: str | None = Query(default=None, description="กรองตาม HTS code"),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """แสดงรายการการคำนวณทั้งหมด เรียงตามเวลาล่าสุดก่อน ใช้สำหรับ audit trail"""
    from app.services.audit_service import AuditService
    service = AuditService(db)
    return await service.list_calculations(hts_code, limit, offset)


@router.get("/calculations/{calculation_id}", response_model=CalculationLogResponse, summary="ดูรายละเอียดการคำนวณ")
async def get_calculation(
    calculation_id: str,
    db: AsyncSession = Depends(get_db),
):
    """ดึงข้อมูลการคำนวณครั้งเดียว ประกอบด้วย input, matched rules, exclusions, ผลลัพธ์"""
    from app.services.audit_service import AuditService
    service = AuditService(db)
    return await service.get_calculation(calculation_id)
