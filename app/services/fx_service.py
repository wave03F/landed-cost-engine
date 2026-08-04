"""
FX Rate Service with live API fallback.

Lookup order:
1. Check database for exact date match
2. Check database for nearest preceding date
3. (If both fail) Fetch live rate from free API and cache it
"""

from datetime import date

import httpx
from fastapi import HTTPException
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fx_rate import FXRate
from app.schemas.fx import FXRateCreate


# Free FX API (no API key required, ~250 req/month)
LIVE_FX_API_URL = "https://api.exchangerate.host/convert"
# Backup: frankfurter.app (open source, no key needed)
BACKUP_FX_API_URL = "https://api.frankfurter.app"


class FXService:
    """Service for FX rate management and lookup with live API fallback."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_rate(self, from_currency: str, to_currency: str, target_date: date) -> FXRate:
        """
        Get the FX rate for a currency pair on a specific date.
        Falls back to the nearest preceding date if exact date not available.
        Raises 404 if no rate found at all.
        """
        rate = await self._get_from_db(from_currency, to_currency, target_date)
        if rate:
            return rate

        raise HTTPException(
            status_code=404,
            detail=f"No FX rate found for {from_currency}/{to_currency} on or before {target_date}",
        )

    async def get_rate_with_fallback(
        self, from_currency: str, to_currency: str, target_date: date
    ) -> tuple["FXRate", str]:
        """
        Get rate with live API fallback. Returns (rate, source).
        source is "database" or "live_api".
        """
        # Try database first
        rate = await self._get_from_db(from_currency, to_currency, target_date)
        if rate:
            return rate, "database"

        # Try live API
        live_rate = await self._fetch_live_rate(from_currency, to_currency, target_date)
        if live_rate:
            # Cache it in database for future use
            cached = FXRate(
                from_currency=from_currency,
                to_currency=to_currency,
                rate=live_rate,
                date=target_date,
            )
            self.db.add(cached)
            await self.db.flush()
            return cached, "live_api"

        raise HTTPException(
            status_code=404,
            detail=f"No FX rate found for {from_currency}/{to_currency} on {target_date} (database and live API both failed)",
        )

    async def _get_from_db(self, from_currency: str, to_currency: str, target_date: date) -> FXRate | None:
        """Try exact date, then nearest preceding date."""
        # Exact date
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

        # Nearest preceding date
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
        return result.scalar_one_or_none()

    async def _fetch_live_rate(
        self, from_currency: str, to_currency: str, target_date: date
    ) -> float | None:
        """
        Fetch rate from free API. Tries frankfurter.app (no key needed).
        Returns the rate as float, or None if failed.
        """
        try:
            # Frankfurter API: GET /2026-08-01?from=CNY&to=USD
            url = f"{BACKUP_FX_API_URL}/{target_date}?from={from_currency}&to={to_currency}"
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    rates = data.get("rates", {})
                    rate = rates.get(to_currency)
                    if rate:
                        return float(rate)
        except Exception:
            pass  # API unavailable — fall through

        return None

    # =========================================================================
    # CRUD operations
    # =========================================================================

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
