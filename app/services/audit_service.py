from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calculation_log import CalculationLog


class AuditService:
    """Service for querying calculation history (audit trail)."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_calculations(
        self,
        hts_code: str | None,
        limit: int,
        offset: int,
        user_id: str | None = None,
    ) -> list[CalculationLog]:
        stmt = select(CalculationLog)
        if hts_code:
            stmt = stmt.where(CalculationLog.hts_code == hts_code)
        if user_id is not None:
            stmt = stmt.where(CalculationLog.user_id == user_id)
        stmt = stmt.order_by(CalculationLog.calculated_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_calculation(self, calculation_id: str) -> CalculationLog:
        stmt = select(CalculationLog).where(CalculationLog.id == calculation_id)
        result = await self.db.execute(stmt)
        log = result.scalar_one_or_none()
        if not log:
            raise HTTPException(status_code=404, detail=f"Calculation '{calculation_id}' not found")
        return log
