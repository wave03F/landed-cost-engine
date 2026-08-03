"""
Unit tests for HTS Code Service.

Tests cover:
- Level detection from code format
- Search by prefix and keyword
- Exact code lookup
- Duplicate prevention
- Validation
"""

import pytest
from app.services.hts_service import HTSService


class TestHTSLevelDetection:
    """Test automatic level detection from code format."""

    def test_two_digit_is_chapter(self):
        service = HTSService.__new__(HTSService)
        assert service._determine_level("84") == "chapter"

    def test_four_digit_is_heading(self):
        service = HTSService.__new__(HTSService)
        assert service._determine_level("8483") == "heading"

    def test_six_digit_with_dot_is_subheading(self):
        service = HTSService.__new__(HTSService)
        assert service._determine_level("8483.40") == "subheading"

    def test_six_digit_without_dot_is_subheading(self):
        service = HTSService.__new__(HTSService)
        assert service._determine_level("848340") == "subheading"

    def test_single_digit_is_chapter(self):
        service = HTSService.__new__(HTSService)
        assert service._determine_level("8") == "chapter"


class TestHTSSearch:
    """Test HTS code search functionality."""

    @pytest.mark.asyncio
    async def test_search_by_prefix(self, seeded_session):
        service = HTSService(seeded_session)
        results = await service.search("8483", None)
        assert len(results) >= 1
        assert all("8483" in r.code for r in results)

    @pytest.mark.asyncio
    async def test_search_by_keyword(self, seeded_session):
        service = HTSService(seeded_session)
        results = await service.search("gear", None)
        assert len(results) >= 1
        assert any("gear" in r.description.lower() for r in results)

    @pytest.mark.asyncio
    async def test_search_filter_by_level(self, seeded_session):
        service = HTSService(seeded_session)
        results = await service.search("", "chapter")
        assert len(results) >= 2
        assert all(r.level == "chapter" for r in results)

    @pytest.mark.asyncio
    async def test_search_empty_query_returns_all(self, seeded_session):
        service = HTSService(seeded_session)
        results = await service.search("", None)
        assert len(results) >= 10  # We seeded 15 codes

    @pytest.mark.asyncio
    async def test_search_no_results(self, seeded_session):
        service = HTSService(seeded_session)
        results = await service.search("9999", None)
        assert len(results) == 0


class TestHTSLookup:
    """Test exact HTS code lookup."""

    @pytest.mark.asyncio
    async def test_get_existing_code(self, seeded_session):
        service = HTSService(seeded_session)
        result = await service.get_by_code("8483.40")
        assert result.code == "8483.40"
        assert result.level == "subheading"
        assert "gear" in result.description.lower()

    @pytest.mark.asyncio
    async def test_get_nonexistent_code_raises_404(self, seeded_session):
        from fastapi import HTTPException
        service = HTSService(seeded_session)
        with pytest.raises(HTTPException) as exc_info:
            await service.get_by_code("9999.99")
        assert exc_info.value.status_code == 404


class TestHTSValidation:
    """Test HTS code existence validation."""

    @pytest.mark.asyncio
    async def test_validate_exact_match(self, seeded_session):
        service = HTSService(seeded_session)
        assert await service.validate_code_exists("8483.40") is True

    @pytest.mark.asyncio
    async def test_validate_heading_match(self, seeded_session):
        service = HTSService(seeded_session)
        assert await service.validate_code_exists("8483") is True

    @pytest.mark.asyncio
    async def test_validate_nonexistent(self, seeded_session):
        service = HTSService(seeded_session)
        assert await service.validate_code_exists("9999.99") is False


class TestHTSCreate:
    """Test HTS code creation."""

    @pytest.mark.asyncio
    async def test_create_new_code(self, seeded_session):
        from app.schemas.hts import HTSCodeCreate
        service = HTSService(seeded_session)
        data = HTSCodeCreate(code="8485", description="Test heading", parent_code="84")
        result = await service.create(data)
        assert result.code == "8485"
        assert result.level == "heading"

    @pytest.mark.asyncio
    async def test_create_duplicate_raises_409(self, seeded_session):
        from fastapi import HTTPException
        from app.schemas.hts import HTSCodeCreate
        service = HTSService(seeded_session)
        data = HTSCodeCreate(code="8483.40", description="Duplicate", parent_code="8483")
        with pytest.raises(HTTPException) as exc_info:
            await service.create(data)
        assert exc_info.value.status_code == 409
