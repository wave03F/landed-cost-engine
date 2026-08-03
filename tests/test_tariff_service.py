"""
Unit tests for Tariff Rule Service.

Tests cover:
- Rule CRUD operations
- Exclusion CRUD operations
- Validation (invalid tariff types)
- Filtering
"""

import pytest
from datetime import date
from fastapi import HTTPException

from app.services.tariff_service import TariffService
from app.schemas.tariff import TariffRuleCreate, TariffRuleUpdate, ExclusionCreate


class TestTariffRuleList:
    """Test tariff rule listing and filtering."""

    @pytest.mark.asyncio
    async def test_list_all_rules(self, seeded_session):
        service = TariffService(seeded_session)
        rules = await service.list_rules(None, None)
        assert len(rules) >= 10  # MFN + 301 + 232 + IEEPA

    @pytest.mark.asyncio
    async def test_filter_by_type(self, seeded_session):
        service = TariffService(seeded_session)
        rules = await service.list_rules("SECTION_301", None)
        assert all(r.tariff_type == "SECTION_301" for r in rules)
        assert len(rules) == 4  # 4 Section 301 rules seeded

    @pytest.mark.asyncio
    async def test_filter_by_hts_code(self, seeded_session):
        service = TariffService(seeded_session)
        rules = await service.list_rules(None, "8483")
        assert all(r.hts_code_pattern == "8483" for r in rules)

    @pytest.mark.asyncio
    async def test_filter_combined(self, seeded_session):
        service = TariffService(seeded_session)
        rules = await service.list_rules("MFN", "8483")
        assert len(rules) == 1
        assert rules[0].rate == 0.025


class TestTariffRuleCreate:
    """Test tariff rule creation."""

    @pytest.mark.asyncio
    async def test_create_valid_rule(self, seeded_session):
        service = TariffService(seeded_session)
        data = TariffRuleCreate(
            tariff_type="SECTION_301",
            hts_code_pattern="8507",
            origin_country="CN",
            rate=0.25,
            effective_from=date(2024, 8, 1),
            stacks_with=["MFN"],
            mutually_exclusive_with=["IEEPA"],
            description="Test rule",
            source_reference="Test ref",
        )
        result = await service.create_rule(data)
        assert result.tariff_type == "SECTION_301"
        assert result.rate == 0.25
        assert result.id is not None

    @pytest.mark.asyncio
    async def test_create_invalid_type_raises_400(self, seeded_session):
        service = TariffService(seeded_session)
        data = TariffRuleCreate(
            tariff_type="INVALID_TYPE",
            hts_code_pattern="8483",
            origin_country="CN",
            rate=0.10,
            effective_from=date(2024, 1, 1),
        )
        with pytest.raises(HTTPException) as exc_info:
            await service.create_rule(data)
        assert exc_info.value.status_code == 400


class TestTariffRuleUpdate:
    """Test tariff rule updates."""

    @pytest.mark.asyncio
    async def test_update_rate(self, seeded_session):
        service = TariffService(seeded_session)
        data = TariffRuleUpdate(rate=0.30)
        result = await service.update_rule("301-8483", data)
        assert result.rate == 0.30

    @pytest.mark.asyncio
    async def test_update_description(self, seeded_session):
        service = TariffService(seeded_session)
        data = TariffRuleUpdate(description="Updated description")
        result = await service.update_rule("mfn-8483", data)
        assert result.description == "Updated description"

    @pytest.mark.asyncio
    async def test_update_nonexistent_raises_404(self, seeded_session):
        service = TariffService(seeded_session)
        data = TariffRuleUpdate(rate=0.10)
        with pytest.raises(HTTPException) as exc_info:
            await service.update_rule("nonexistent-id", data)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_update_effective_to(self, seeded_session):
        service = TariffService(seeded_session)
        data = TariffRuleUpdate(effective_to=date(2026, 12, 31))
        result = await service.update_rule("301-8483", data)
        assert result.effective_to == date(2026, 12, 31)


class TestExclusionList:
    """Test exclusion listing."""

    @pytest.mark.asyncio
    async def test_list_all_exclusions(self, seeded_session):
        service = TariffService(seeded_session)
        exclusions = await service.list_exclusions(None)
        assert len(exclusions) == 2  # 2 seeded

    @pytest.mark.asyncio
    async def test_list_filter_by_hts_code(self, seeded_session):
        service = TariffService(seeded_session)
        exclusions = await service.list_exclusions("8542.31")
        assert len(exclusions) == 1
        assert exclusions[0].tariff_type == "IEEPA"


class TestExclusionCreate:
    """Test exclusion creation."""

    @pytest.mark.asyncio
    async def test_create_valid_exclusion(self, seeded_session):
        service = TariffService(seeded_session)
        data = ExclusionCreate(
            hts_code="8501.52",
            tariff_type="SECTION_301",
            origin_country="CN",
            effective_from=date(2025, 1, 1),
            effective_to=date(2025, 6, 30),
            description="Test exclusion",
        )
        result = await service.create_exclusion(data)
        assert result.hts_code == "8501.52"
        assert result.tariff_type == "SECTION_301"

    @pytest.mark.asyncio
    async def test_create_invalid_type_raises_400(self, seeded_session):
        service = TariffService(seeded_session)
        data = ExclusionCreate(
            hts_code="8483.40",
            tariff_type="FAKE_TYPE",
            effective_from=date(2025, 1, 1),
        )
        with pytest.raises(HTTPException) as exc_info:
            await service.create_exclusion(data)
        assert exc_info.value.status_code == 400
