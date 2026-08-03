"""
Unit tests for FX Rate Service.

Tests cover:
- Exact date rate lookup
- Nearest preceding date fallback
- Rate not found error
- Rate creation (upsert)
- List with date filtering
"""

import pytest
from datetime import date
from fastapi import HTTPException

from app.services.fx_service import FXService
from app.schemas.fx import FXRateCreate


class TestFXRateLookup:
    """Test FX rate retrieval logic."""

    @pytest.mark.asyncio
    async def test_exact_date_match(self, seeded_session):
        service = FXService(seeded_session)
        rate = await service.get_rate("CNY", "USD", date(2026, 8, 1))
        assert rate.rate == 0.1389
        assert rate.date == date(2026, 8, 1)

    @pytest.mark.asyncio
    async def test_fallback_to_nearest_preceding(self, seeded_session):
        """If no exact match, use the nearest earlier date."""
        service = FXService(seeded_session)
        # No rate for July 15, should fall back to July 1
        rate = await service.get_rate("CNY", "USD", date(2026, 7, 15))
        assert rate.rate == 0.1380
        assert rate.date == date(2026, 7, 1)

    @pytest.mark.asyncio
    async def test_fallback_across_months(self, seeded_session):
        """Fallback should work across month boundaries."""
        service = FXService(seeded_session)
        # No rate in Feb 2025, should fall back to Jan 1, 2025
        rate = await service.get_rate("CNY", "USD", date(2025, 2, 15))
        assert rate.rate == 0.1395

    @pytest.mark.asyncio
    async def test_no_rate_found_raises_404(self, seeded_session):
        """If no rate exists at all before the date, raise 404."""
        service = FXService(seeded_session)
        with pytest.raises(HTTPException) as exc_info:
            await service.get_rate("CNY", "USD", date(2010, 1, 1))
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_no_rate_for_unknown_pair(self, seeded_session):
        """Unknown currency pair should raise 404."""
        service = FXService(seeded_session)
        with pytest.raises(HTTPException) as exc_info:
            await service.get_rate("EUR", "USD", date(2026, 8, 1))
        assert exc_info.value.status_code == 404


class TestFXRateCreate:
    """Test FX rate creation/upsert."""

    @pytest.mark.asyncio
    async def test_create_new_rate(self, seeded_session):
        service = FXService(seeded_session)
        data = FXRateCreate(
            from_currency="CNY", to_currency="USD",
            rate=0.1400, rate_date=date(2026, 9, 1)
        )
        result = await service.create_rate(data)
        assert result.rate == 0.1400
        assert result.date == date(2026, 9, 1)

    @pytest.mark.asyncio
    async def test_upsert_existing_rate(self, seeded_session):
        """Creating a rate for an existing date should update it."""
        service = FXService(seeded_session)
        data = FXRateCreate(
            from_currency="CNY", to_currency="USD",
            rate=0.1500, rate_date=date(2026, 8, 1)
        )
        result = await service.create_rate(data)
        assert result.rate == 0.1500  # Updated

    @pytest.mark.asyncio
    async def test_create_different_currency_pair(self, seeded_session):
        service = FXService(seeded_session)
        data = FXRateCreate(
            from_currency="EUR", to_currency="USD",
            rate=1.0850, rate_date=date(2026, 8, 1)
        )
        result = await service.create_rate(data)
        assert result.from_currency == "EUR"
        assert result.rate == 1.0850


class TestFXRateList:
    """Test FX rate listing."""

    @pytest.mark.asyncio
    async def test_list_all_rates(self, seeded_session):
        service = FXService(seeded_session)
        results = await service.list_rates("CNY", "USD", None, None)
        assert len(results) == 7  # We seeded 7 CNY/USD rates

    @pytest.mark.asyncio
    async def test_list_with_date_filter(self, seeded_session):
        service = FXService(seeded_session)
        results = await service.list_rates("CNY", "USD", date(2026, 7, 1), date(2026, 8, 1))
        assert len(results) == 3  # Jul 1, Jul 31, Aug 1

    @pytest.mark.asyncio
    async def test_list_empty_for_unknown_pair(self, seeded_session):
        service = FXService(seeded_session)
        results = await service.list_rates("JPY", "USD", None, None)
        assert len(results) == 0
