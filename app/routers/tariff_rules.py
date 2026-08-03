from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_api_key
from app.database import get_db
from app.schemas.tariff import (
    TariffRuleResponse, TariffRuleCreate, TariffRuleUpdate,
    ExclusionResponse, ExclusionCreate,
)

router = APIRouter(dependencies=[Depends(require_api_key)])


@router.get("/tariff-rules", response_model=list[TariffRuleResponse], summary="ดูรายการกฎภาษีทั้งหมด")
async def list_tariff_rules(
    tariff_type: str | None = Query(default=None, description="กรอง: MFN, SECTION_301, SECTION_232, IEEPA"),
    hts_code: str | None = Query(default=None, description="กรองตาม HTS code pattern"),
    db: AsyncSession = Depends(get_db),
):
    """แสดงกฎภาษีทั้งหมดพร้อม temporal versioning"""
    from app.services.tariff_service import TariffService
    service = TariffService(db)
    return await service.list_rules(tariff_type, hts_code)


@router.post("/tariff-rules", response_model=TariffRuleResponse, status_code=201, summary="สร้างกฎภาษีใหม่")
async def create_tariff_rule(
    data: TariffRuleCreate,
    db: AsyncSession = Depends(get_db),
):
    """เพิ่มกฎภาษีใหม่พร้อมตั้ง stacking/mutual-exclusion config"""
    from app.services.tariff_service import TariffService
    service = TariffService(db)
    return await service.create_rule(data)


@router.put("/tariff-rules/{rule_id}", response_model=TariffRuleResponse, summary="แก้ไขกฎภาษี")
async def update_tariff_rule(
    rule_id: str,
    data: TariffRuleUpdate,
    db: AsyncSession = Depends(get_db),
):
    """อัปเดตกฎภาษีที่มีอยู่ เฉพาะ field ที่ส่งมาจะถูกแก้ไข"""
    from app.services.tariff_service import TariffService
    service = TariffService(db)
    return await service.update_rule(rule_id, data)


@router.get("/exclusions", response_model=list[ExclusionResponse], summary="ดูรายการข้อยกเว้นภาษี")
async def list_exclusions(
    hts_code: str | None = Query(default=None, description="กรองตาม HTS code"),
    db: AsyncSession = Depends(get_db),
):
    """แสดง exclusion ทั้งหมด (ทั้งที่ยังมีผลและหมดอายุ)"""
    from app.services.tariff_service import TariffService
    service = TariffService(db)
    return await service.list_exclusions(hts_code)


@router.post("/exclusions", response_model=ExclusionResponse, status_code=201, summary="สร้างข้อยกเว้นภาษีใหม่")
async def create_exclusion(
    data: ExclusionCreate,
    db: AsyncSession = Depends(get_db),
):
    """เพิ่ม exclusion ใหม่ ตั้ง effective_to เป็น null สำหรับยกเว้นถาวร"""
    from app.services.tariff_service import TariffService
    service = TariffService(db)
    return await service.create_exclusion(data)
