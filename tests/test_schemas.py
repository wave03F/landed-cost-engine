"""
Unit tests for Pydantic schemas (validation).

Tests cover:
- Required field enforcement
- Field validation (min/max, format)
- Default values
- Invalid input rejection
"""

import pytest
from datetime import date
from pydantic import ValidationError

from app.schemas.calculation import CalculationRequest
from app.schemas.tariff import TariffRuleCreate, ExclusionCreate
from app.schemas.hts import HTSCodeCreate


class TestCalculationRequestValidation:
    """Test CalculationRequest input validation."""

    def test_valid_cny_request(self):
        req = CalculationRequest(
            hts_code="8483.40",
            invoice_value_cny=50000,
            origin_country="CN",
            import_date=date(2026, 8, 1),
            freight_usd=800,
            insurance_usd=50,
        )
        assert req.invoice_value_cny == 50000
        assert req.invoice_value_usd is None

    def test_valid_usd_request(self):
        req = CalculationRequest(
            hts_code="8483.40",
            invoice_value_usd=7000,
            import_date=date(2026, 8, 1),
        )
        assert req.invoice_value_usd == 7000
        assert req.origin_country == "CN"  # default

    def test_defaults_applied(self):
        req = CalculationRequest(
            hts_code="8483.40",
            invoice_value_usd=1000,
            import_date=date(2026, 8, 1),
        )
        assert req.origin_country == "CN"
        assert req.freight_usd == 0
        assert req.insurance_usd == 0

    def test_missing_hts_code_raises(self):
        with pytest.raises(ValidationError):
            CalculationRequest(
                invoice_value_usd=1000,
                import_date=date(2026, 8, 1),
            )

    def test_missing_import_date_raises(self):
        with pytest.raises(ValidationError):
            CalculationRequest(
                hts_code="8483.40",
                invoice_value_usd=1000,
            )

    def test_negative_freight_raises(self):
        with pytest.raises(ValidationError):
            CalculationRequest(
                hts_code="8483.40",
                invoice_value_usd=1000,
                import_date=date(2026, 8, 1),
                freight_usd=-100,
            )

    def test_negative_insurance_raises(self):
        with pytest.raises(ValidationError):
            CalculationRequest(
                hts_code="8483.40",
                invoice_value_usd=1000,
                import_date=date(2026, 8, 1),
                insurance_usd=-5,
            )


class TestTariffRuleCreateValidation:
    """Test TariffRuleCreate validation."""

    def test_valid_rule(self):
        rule = TariffRuleCreate(
            tariff_type="SECTION_301",
            hts_code_pattern="8483",
            rate=0.25,
            effective_from=date(2018, 7, 6),
        )
        assert rule.tariff_type == "SECTION_301"
        assert rule.stacks_with == []
        assert rule.mutually_exclusive_with == []

    def test_rate_too_high_raises(self):
        with pytest.raises(ValidationError):
            TariffRuleCreate(
                tariff_type="MFN",
                hts_code_pattern="84",
                rate=6.0,  # max is 5.0
                effective_from=date(2020, 1, 1),
            )

    def test_negative_rate_raises(self):
        with pytest.raises(ValidationError):
            TariffRuleCreate(
                tariff_type="MFN",
                hts_code_pattern="84",
                rate=-0.1,
                effective_from=date(2020, 1, 1),
            )

    def test_missing_effective_from_raises(self):
        with pytest.raises(ValidationError):
            TariffRuleCreate(
                tariff_type="MFN",
                hts_code_pattern="84",
                rate=0.02,
            )


class TestExclusionCreateValidation:
    """Test ExclusionCreate validation."""

    def test_valid_exclusion(self):
        exc = ExclusionCreate(
            hts_code="8542.31",
            tariff_type="IEEPA",
            effective_from=date(2025, 4, 9),
        )
        assert exc.origin_country == "CN"  # default
        assert exc.effective_to is None

    def test_missing_hts_code_raises(self):
        with pytest.raises(ValidationError):
            ExclusionCreate(
                tariff_type="IEEPA",
                effective_from=date(2025, 1, 1),
            )


class TestHTSCodeCreateValidation:
    """Test HTSCodeCreate validation."""

    def test_valid_create(self):
        hts = HTSCodeCreate(
            code="8483.90",
            description="Toothed wheels and parts",
            parent_code="8483",
        )
        assert hts.code == "8483.90"

    def test_missing_code_raises(self):
        with pytest.raises(ValidationError):
            HTSCodeCreate(description="Missing code")

    def test_missing_description_raises(self):
        with pytest.raises(ValidationError):
            HTSCodeCreate(code="8483.90")
