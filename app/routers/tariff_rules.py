from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_api_key, require_admin
from app.database import get_db
from app.schemas.tariff import (
    TariffRuleResponse, TariffRuleCreate, TariffRuleUpdate,
    ExclusionResponse, ExclusionCreate, ExclusionUpdate,
    CloseRequest,
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


@router.post(
    "/tariff-rules",
    response_model=TariffRuleResponse,
    status_code=201,
    summary="สร้างกฎภาษีใหม่ (admin)",
    dependencies=[Depends(require_admin)],
)
async def create_tariff_rule(
    data: TariffRuleCreate,
    db: AsyncSession = Depends(get_db),
):
    """เพิ่มกฎภาษีใหม่พร้อมตั้ง stacking/mutual-exclusion config (ต้องเป็น admin)"""
    from app.services.tariff_service import TariffService
    service = TariffService(db)
    return await service.create_rule(data)


@router.put(
    "/tariff-rules/{rule_id}",
    response_model=TariffRuleResponse,
    summary="แก้ไขกฎภาษี (admin)",
    dependencies=[Depends(require_admin)],
)
async def update_tariff_rule(
    rule_id: str,
    data: TariffRuleUpdate,
    db: AsyncSession = Depends(get_db),
):
    """อัปเดตกฎภาษีที่มีอยู่ เฉพาะ field ที่ส่งมาจะถูกแก้ไข (ต้องเป็น admin)"""
    from app.services.tariff_service import TariffService
    service = TariffService(db)
    return await service.update_rule(rule_id, data)


@router.delete(
    "/tariff-rules/{rule_id}",
    status_code=204,
    summary="ลบกฎภาษี (admin)",
    dependencies=[Depends(require_admin)],
)
async def delete_tariff_rule(
    rule_id: str,
    db: AsyncSession = Depends(get_db),
):
    """ลบกฎภาษี (ต้องเป็น admin). คืน 404 ถ้าไม่พบ.

    เฉพาะกฎที่ **ยังไม่เคยมีผล** (effective_from อยู่ในอนาคต) จึงจะลบได้.
    กฎที่มีผลแล้วจะได้ 409 — ให้ใช้ POST /tariff-rules/{id}/close แทน
    เพื่อรักษาประวัติ audit ไว้."""
    from app.services.tariff_service import TariffService
    service = TariffService(db)
    await service.delete_rule(rule_id)


@router.post(
    "/tariff-rules/{rule_id}/close",
    response_model=TariffRuleResponse,
    summary="ปิดกฎภาษี (soft-close, admin)",
    dependencies=[Depends(require_admin)],
)
async def close_tariff_rule(
    rule_id: str,
    data: CloseRequest,
    db: AsyncSession = Depends(get_db),
):
    """ตั้งวันสิ้นสุด (effective_to) ให้กฎภาษี แทนการลบทิ้ง.

    ใช้สำหรับ "ปิด" กฎที่เคยหรือกำลังมีผล โดยไม่ลบออกจากระบบ
    เพื่อรักษา audit trail. หลังจากวันที่กำหนด กฎจะไม่ถูกนำไปใช้ในการคำนวณอีก
    (ต้องเป็น admin)."""
    from app.services.tariff_service import TariffService
    service = TariffService(db)
    return await service.close_rule(rule_id, data)


@router.get("/exclusions", response_model=list[ExclusionResponse], summary="ดูรายการข้อยกเว้นภาษี")
async def list_exclusions(
    hts_code: str | None = Query(default=None, description="กรองตาม HTS code"),
    db: AsyncSession = Depends(get_db),
):
    """แสดง exclusion ทั้งหมด (ทั้งที่ยังมีผลและหมดอายุ)"""
    from app.services.tariff_service import TariffService
    service = TariffService(db)
    return await service.list_exclusions(hts_code)


@router.post(
    "/exclusions",
    response_model=ExclusionResponse,
    status_code=201,
    summary="สร้างข้อยกเว้นภาษีใหม่ (admin)",
    dependencies=[Depends(require_admin)],
)
async def create_exclusion(
    data: ExclusionCreate,
    db: AsyncSession = Depends(get_db),
):
    """เพิ่ม exclusion ใหม่ ตั้ง effective_to เป็น null สำหรับยกเว้นถาวร (ต้องเป็น admin)"""
    from app.services.tariff_service import TariffService
    service = TariffService(db)
    return await service.create_exclusion(data)


@router.put(
    "/exclusions/{exclusion_id}",
    response_model=ExclusionResponse,
    summary="แก้ไขข้อยกเว้นภาษี (admin)",
    dependencies=[Depends(require_admin)],
)
async def update_exclusion(
    exclusion_id: str,
    data: ExclusionUpdate,
    db: AsyncSession = Depends(get_db),
):
    """อัปเดต exclusion เฉพาะ field ที่ส่งมาจะถูกแก้ไข (ต้องเป็น admin)"""
    from app.services.tariff_service import TariffService
    service = TariffService(db)
    return await service.update_exclusion(exclusion_id, data)


@router.delete(
    "/exclusions/{exclusion_id}",
    status_code=204,
    summary="ลบข้อยกเว้นภาษี (admin)",
    dependencies=[Depends(require_admin)],
)
async def delete_exclusion(
    exclusion_id: str,
    db: AsyncSession = Depends(get_db),
):
    """ลบ exclusion (ต้องเป็น admin). คืน 404 ถ้าไม่พบ.

    เฉพาะ exclusion ที่ **ยังไม่เคยมีผล** จึงจะลบได้.
    ที่มีผลแล้วจะได้ 409 — ให้ใช้ POST /exclusions/{id}/close แทน."""
    from app.services.tariff_service import TariffService
    service = TariffService(db)
    await service.delete_exclusion(exclusion_id)


@router.post(
    "/exclusions/{exclusion_id}/close",
    response_model=ExclusionResponse,
    summary="ปิดข้อยกเว้นภาษี (soft-close, admin)",
    dependencies=[Depends(require_admin)],
)
async def close_exclusion(
    exclusion_id: str,
    data: CloseRequest,
    db: AsyncSession = Depends(get_db),
):
    """ตั้งวันสิ้นสุด (effective_to) ให้ exclusion แทนการลบทิ้ง เพื่อรักษา audit trail
    (ต้องเป็น admin)."""
    from app.services.tariff_service import TariffService
    service = TariffService(db)
    return await service.close_exclusion(exclusion_id, data)
