from datetime import date

from fastapi import HTTPException
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fx_rate import FXRate
from app.schemas.fx import FXRateCreate


class FXService:
    """Service for FX rate management and lookup."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_rate(self, from_currency: str, to_currency: str, target_date: date) -> FXRate:
        """
        Get the FX rate for a currency pair on a specific date.
        Falls back to the nearest preceding date if exact date not available.
        """
        # Try exact date first
        stmt = select(FXRate).where(
            and_(
                FXRate.from_currency == from_currency,
                FXRate.to_currency == to_currency,
                FXRate.date == target_date,
            )
        )
        result = await self.db.execute(stmt)
        rate = result.scalar_one_or_none()
        if rate:
            return rate

        # Fall back to nearest preceding date
        stmt = (
            select(FXRate)
            .where(
                and_(
                    FXRate.from_currency == from_currency,
                    FXRate.to_currency == to_currency,
                    FXRate.date <= target_date,
                )
            )
            .order_by(FXRate.date.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        rate = result.scalar_one_or_none()
        if rate:
            return rate

        raise HTTPException(
            status_code=404,
            detail=f"No FX rate found for {from_currency}/{to_currency} on or before {target_date}",
        )

    async def list_rates(
        self,
        from_currency: str,
        to_currency: str,
        date_from: date | None,
        date_to: date | None,
    ) -> list[FXRate]:
        stmt = select(FXRate).where(
            and_(
                FXRate.from_currency == from_currency,
                FXRate.to_currency == to_currency,
            )
        )
        if date_from:
            stmt = stmt.where(FXRate.date >= date_from)
        if date_to:
            stmt = stmt.where(FXRate.date <= date_to)
        stmt = stmt.order_by(FXRate.date.desc()).limit(100)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_rate(self, data: FXRateCreate) -> FXRate:
        # Upsert: check if rate for this pair+date already exists
        stmt = select(FXRate).where(
            and_(
                FXRate.from_currency == data.from_currency,
                FXRate.to_currency == data.to_currency,
                FXRate.date == data.rate_date,
            )
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            existing.rate = data.rate
            await self.db.flush()
            return existing

        rate = FXRate(
            from_currency=data.from_currency,
            to_currency=data.to_currency,
            rate=data.rate,
            date=data.rate_date,
        )
        self.db.add(rate)
        await self.db.flush()
        return rate
