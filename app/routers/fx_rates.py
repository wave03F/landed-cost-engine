from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_api_key, require_admin
from app.database import get_db
from app.schemas.fx import FXRateResponse, FXRateCreate

router = APIRouter(dependencies=[Depends(require_api_key)])


@router.get("/fx-rates", response_model=list[FXRateResponse], summary="ดูอัตราแลกเปลี่ยนย้อนหลัง")
async def list_fx_rates(
    from_currency: str = Query(default="CNY"),
    to_currency: str = Query(default="USD"),
    date_from: date | None = None,
    date_to: date | None = None,
    db: AsyncSession = Depends(get_db),
):
    """แสดงอัตราแลกเปลี่ยนสำหรับคู่สกุลเงิน พร้อม filter ตามช่วงวันที่"""
    from app.services.fx_service import FXService
    service = FXService(db)
    return await service.list_rates(from_currency, to_currency, date_from, date_to)


@router.post(
    "/fx-rates",
    response_model=FXRateResponse,
    status_code=201,
    summary="เพิ่ม/อัปเดตอัตราแลกเปลี่ยน (admin)",
    dependencies=[Depends(require_admin)],
)
async def create_fx_rate(
    data: FXRateCreate,
    db: AsyncSession = Depends(get_db),
):
    """เพิ่มอัตราแลกเปลี่ยนสำหรับวันที่ระบุ (upsert ถ้ามีอยู่แล้ว) (ต้องเป็น admin)"""
    from app.services.fx_service import FXService
    service = FXService(db)
    return await service.create_rate(data)


@router.delete(
    "/fx-rates/{rate_id}",
    status_code=204,
    summary="ลบอัตราแลกเปลี่ยน (admin)",
    dependencies=[Depends(require_admin)],
)
async def delete_fx_rate(
    rate_id: str,
    db: AsyncSession = Depends(get_db),
):
    """ลบอัตราแลกเปลี่ยนตาม id (ต้องเป็น admin). คืน 404 ถ้าไม่พบ"""
    from app.services.fx_service import FXService
    service = FXService(db)
    await service.delete_rate(rate_id)
