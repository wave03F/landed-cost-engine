from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import authenticate, Identity
from app.database import get_db
from app.schemas.calculation import CalculationRequest, CalculationResponse
from app.services.calculation_service import CalculationService

router = APIRouter()


@router.post("/calculate", response_model=CalculationResponse, summary="คำนวณ Landed Cost")
async def calculate_landed_cost(
    request: CalculationRequest,
    identity: Identity = Depends(authenticate),
    db: AsyncSession = Depends(get_db),
):
    """
    คำนวณต้นทุนนำเข้ารวม (Landed Cost) สำหรับสินค้า 1 รายการ

    ขั้นตอน:
    1. ตรวจสอบสิทธิ์ + โควตาการคำนวณต่อวัน (เฉพาะผู้ใช้ที่ล็อกอิน)
    2. ตรวจสอบ HTS code
    3. แปลงสกุลเงิน CNY → USD (ถ้าจำเป็น)
    4. คำนวณ Customs Value (CIF)
    5. ดึงกฎภาษีที่มีผล ณ วันที่นำเข้า
    6. ตรวจสอบ Exclusion
    7. ใช้ Stacking Logic
    8. คืน breakdown ทุกชั้นภาษี + Audit ID (ผูกกับผู้ใช้ที่ล็อกอิน)
    """
    service = CalculationService(db)
    return await service.calculate(request, identity=identity)
