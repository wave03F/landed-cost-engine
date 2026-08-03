from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_api_key
from app.database import get_db
from app.schemas.calculation import CalculationRequest, CalculationResponse
from app.services.calculation_service import CalculationService

router = APIRouter(dependencies=[Depends(require_api_key)])


@router.post("/calculate", response_model=CalculationResponse, summary="คำนวณ Landed Cost")
async def calculate_landed_cost(
    request: CalculationRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    คำนวณต้นทุนนำเข้ารวม (Landed Cost) สำหรับสินค้า 1 รายการ

    ขั้นตอน:
    1. ตรวจสอบ HTS code
    2. แปลงสกุลเงิน CNY → USD (ถ้าจำเป็น)
    3. คำนวณ Customs Value (CIF)
    4. ดึงกฎภาษีที่มีผล ณ วันที่นำเข้า
    5. ตรวจสอบ Exclusion
    6. ใช้ Stacking Logic
    7. คืน breakdown ทุกชั้นภาษี + Audit ID
    """
    service = CalculationService(db)
    return await service.calculate(request)
