from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_api_key, require_admin
from app.database import get_db
from app.schemas.hts import HTSCodeResponse, HTSCodeCreate, HTSCodeUpdate
from app.services.hts_service import HTSService

router = APIRouter(dependencies=[Depends(require_api_key)])


@router.get("/hts-codes", response_model=list[HTSCodeResponse], summary="ค้นหารหัส HTS")
async def search_hts_codes(
    q: str = Query(default="", description="ค้นหาตาม prefix ของรหัส หรือ keyword ในคำอธิบาย"),
    level: str | None = Query(default=None, description="กรองตามระดับ: chapter, heading, subheading"),
    db: AsyncSession = Depends(get_db),
):
    """ค้นหารหัสพิกัดศุลกากร (HTS) รองรับ prefix matching และ keyword search"""
    service = HTSService(db)
    return await service.search(q, level)


@router.get("/hts-codes/{code}", response_model=HTSCodeResponse, summary="ดูรายละเอียด HTS code")
async def get_hts_code(code: str, db: AsyncSession = Depends(get_db)):
    """ดึงข้อมูลรหัส HTS ที่ระบุ คืน 404 ถ้าไม่พบ"""
    service = HTSService(db)
    return await service.get_by_code(code)


@router.post(
    "/hts-codes",
    response_model=HTSCodeResponse,
    status_code=201,
    summary="เพิ่มรหัส HTS ใหม่ (admin)",
    dependencies=[Depends(require_admin)],
)
async def create_hts_code(
    data: HTSCodeCreate,
    db: AsyncSession = Depends(get_db),
):
    """เพิ่มรหัส HTS ใหม่ ระบบกำหนด level อัตโนมัติจากรูปแบบรหัส (ต้องเป็น admin)"""
    service = HTSService(db)
    return await service.create(data)


@router.put(
    "/hts-codes/{code}",
    response_model=HTSCodeResponse,
    summary="แก้ไขรหัส HTS (admin)",
    dependencies=[Depends(require_admin)],
)
async def update_hts_code(
    code: str,
    data: HTSCodeUpdate,
    db: AsyncSession = Depends(get_db),
):
    """อัปเดตคำอธิบาย/parent ของรหัส HTS เฉพาะ field ที่ส่งมาจะถูกแก้ไข (ต้องเป็น admin)"""
    service = HTSService(db)
    return await service.update(code, data)


@router.delete(
    "/hts-codes/{code}",
    status_code=204,
    summary="ลบรหัส HTS (admin)",
    dependencies=[Depends(require_admin)],
)
async def delete_hts_code(
    code: str,
    db: AsyncSession = Depends(get_db),
):
    """ลบรหัส HTS ออกจากระบบ (ต้องเป็น admin). คืน 404 ถ้าไม่พบ"""
    service = HTSService(db)
    await service.delete(code)
