"""
Integration tests for the landed cost calculation API.

Tests the full flow: HTTP request → calculation → response with breakdown.
Covers 15+ scenarios including edge cases per the success criteria.
"""

import pytest
from httpx import AsyncClient


class TestCalculationEndpoint:
    """Integration tests for POST /api/v1/calculate"""

    @pytest.mark.asyncio
    async def test_basic_calculation_cny(self, client: AsyncClient):
        """Scenario 1: Basic CNY calculation with MFN + Section 301."""
        response = await client.post("/calculate", json={
            "hts_code": "8483.40",
            "invoice_value_cny": 50000,
            "origin_country": "CN",
            "import_date": "2026-08-01",
            "freight_usd": 800,
            "insurance_usd": 50,
        })
        assert response.status_code == 200
        data = response.json()

        assert data["hts_code"] == "8483.40"
        assert data["invoice_value_usd"] > 0
        assert data["landed_cost_usd"] > data["customs_value_usd"]
        assert data["fx_rate_used"]["rate"] == 0.1389
        assert data["calculation_id"] is not None

    @pytest.mark.asyncio
    async def test_calculation_usd_direct(self, client: AsyncClient):
        """Scenario 2: Direct USD input (no FX conversion needed)."""
        response = await client.post("/calculate", json={
            "hts_code": "8483.40",
            "invoice_value_usd": 7000,
            "origin_country": "CN",
            "import_date": "2026-08-01",
            "freight_usd": 500,
            "insurance_usd": 30,
        })
        assert response.status_code == 200
        data = response.json()

        assert data["invoice_value_usd"] == 7000
        assert data["customs_value_usd"] == 7530  # 7000 + 500 + 30
        assert data["fx_rate_used"] is None

    @pytest.mark.asyncio
    async def test_pre_301_calculation(self, client: AsyncClient):
        """Scenario 3: Import before Section 301 — only MFN + fees apply."""
        response = await client.post("/calculate", json={
            "hts_code": "8483.40",
            "invoice_value_usd": 10000,
            "origin_country": "CN",
            "import_date": "2017-01-15",
            "freight_usd": 500,
            "insurance_usd": 50,
        })
        assert response.status_code == 200
        data = response.json()

        # MFN + MPF + HMF should apply (no 301/232/IEEPA before 2018)
        applied = [t for t in data["tariff_breakdown"] if t["applied"]]
        applied_types = {t["type"] for t in applied}
        assert "MFN" in applied_types
        assert "MPF" in applied_types
        assert "HMF" in applied_types
        assert "SECTION_301" not in applied_types

    @pytest.mark.asyncio
    async def test_stacking_301_plus_mfn(self, client: AsyncClient):
        """Scenario 4: MFN + Section 301 stacking (post-2018, pre-IEEPA)."""
        response = await client.post("/calculate", json={
            "hts_code": "8501.52",
            "invoice_value_usd": 5000,
            "origin_country": "CN",
            "import_date": "2020-06-01",
            "freight_usd": 300,
            "insurance_usd": 20,
        })
        assert response.status_code == 200
        data = response.json()

        applied = [t for t in data["tariff_breakdown"] if t["applied"]]
        applied_types = {t["type"] for t in applied}
        assert "MFN" in applied_types
        assert "SECTION_301" in applied_types

    @pytest.mark.asyncio
    async def test_ieepa_vs_301_mutual_exclusion(self, client: AsyncClient):
        """Scenario 5: IEEPA and 301 are mutually exclusive — higher wins."""
        response = await client.post("/calculate", json={
            "hts_code": "8483.40",
            "invoice_value_usd": 10000,
            "origin_country": "CN",
            "import_date": "2026-08-01",
            "freight_usd": 500,
            "insurance_usd": 50,
        })
        assert response.status_code == 200
        data = response.json()

        applied_types = {t["type"] for t in data["tariff_breakdown"] if t["applied"]}
        not_applied = [t for t in data["tariff_breakdown"] if not t["applied"]]

        # 301 (25%) > IEEPA (14.5%), so 301 wins
        assert "SECTION_301" in applied_types
        assert any(t["type"] == "IEEPA" and t["reason"] == "excluded_by_stacking_rule" for t in not_applied)

    @pytest.mark.asyncio
    async def test_exclusion_applied(self, client: AsyncClient):
        """Scenario 6: Active exclusion removes a tariff layer."""
        response = await client.post("/calculate", json={
            "hts_code": "8542.31",
            "invoice_value_usd": 20000,
            "origin_country": "CN",
            "import_date": "2026-01-01",
            "freight_usd": 200,
            "insurance_usd": 10,
        })
        assert response.status_code == 200
        data = response.json()

        # IEEPA should be excluded for semiconductors
        assert len(data["exclusions_applied"]) > 0
        assert data["exclusions_applied"][0]["tariff_type"] == "IEEPA"

    @pytest.mark.asyncio
    async def test_expired_exclusion(self, client: AsyncClient):
        """Scenario 7: Expired exclusion — tariff should apply normally."""
        response = await client.post("/calculate", json={
            "hts_code": "8517.12",
            "invoice_value_usd": 500,
            "origin_country": "CN",
            "import_date": "2025-08-01",
            "freight_usd": 20,
            "insurance_usd": 5,
        })
        assert response.status_code == 200
        data = response.json()

        # 301 exclusion expired on 2025-07-09, should NOT be in exclusions
        assert len(data["exclusions_applied"]) == 0

    @pytest.mark.asyncio
    async def test_zero_duty_free_product(self, client: AsyncClient):
        """Scenario 8: Product with 0% MFN — still pays fees (MPF + HMF)."""
        response = await client.post("/calculate", json={
            "hts_code": "8517.12",
            "invoice_value_usd": 1000,
            "origin_country": "CN",
            "import_date": "2017-01-01",
            "freight_usd": 50,
            "insurance_usd": 5,
        })
        assert response.status_code == 200
        data = response.json()

        # MFN is 0% but fees still apply
        assert data["total_duty_usd"] == 0
        assert data["fees"] is not None
        assert data["fees"]["mpf_usd"] > 0
        assert data["landed_cost_usd"] > data["customs_value_usd"]

    @pytest.mark.asyncio
    async def test_section_232_bearing(self, client: AsyncClient):
        """Scenario 9: Ball bearing with Section 232 tariff."""
        response = await client.post("/calculate", json={
            "hts_code": "8482.10",
            "invoice_value_usd": 3000,
            "origin_country": "CN",
            "import_date": "2020-01-01",
            "freight_usd": 200,
            "insurance_usd": 15,
        })
        assert response.status_code == 200
        data = response.json()

        applied_types = {t["type"] for t in data["tariff_breakdown"] if t["applied"]}
        assert "SECTION_232" in applied_types
        assert "MFN" in applied_types

    @pytest.mark.asyncio
    async def test_invalid_hts_code(self, client: AsyncClient):
        """Scenario 10: Invalid HTS code should return 400."""
        response = await client.post("/calculate", json={
            "hts_code": "9999.99",
            "invoice_value_usd": 1000,
            "origin_country": "CN",
            "import_date": "2026-08-01",
            "freight_usd": 100,
            "insurance_usd": 10,
        })
        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_no_value_provided(self, client: AsyncClient):
        """Scenario 11: Missing both CNY and USD value — should error."""
        response = await client.post("/calculate", json={
            "hts_code": "8483.40",
            "origin_country": "CN",
            "import_date": "2026-08-01",
            "freight_usd": 100,
            "insurance_usd": 10,
        })
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_fx_fallback_nearest_date(self, client: AsyncClient):
        """Scenario 12: FX rate not available for exact date — uses nearest previous."""
        response = await client.post("/calculate", json={
            "hts_code": "8483.40",
            "invoice_value_cny": 10000,
            "origin_country": "CN",
            "import_date": "2026-07-15",  # no exact rate, should use 7/1 rate
            "freight_usd": 200,
            "insurance_usd": 10,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["fx_rate_used"]["rate"] == 0.1380  # falls back to July 1

    @pytest.mark.asyncio
    async def test_high_value_shipment(self, client: AsyncClient):
        """Scenario 13: High-value shipment — verify duty math accuracy."""
        response = await client.post("/calculate", json={
            "hts_code": "8504.40",
            "invoice_value_usd": 100000,
            "origin_country": "CN",
            "import_date": "2020-01-01",
            "freight_usd": 5000,
            "insurance_usd": 500,
        })
        assert response.status_code == 200
        data = response.json()

        customs_value = 100000 + 5000 + 500  # 105500
        assert data["customs_value_usd"] == customs_value

        # MFN 1.5% + Section 301 25% = 26.5% of customs value
        expected_mfn = round(customs_value * 0.015, 2)
        expected_301 = round(customs_value * 0.25, 2)
        expected_total_duty = round(expected_mfn + expected_301, 2)

        assert data["total_duty_usd"] == expected_total_duty
        # Landed cost = customs + duty + fees (MPF + HMF)
        assert data["fees"] is not None
        expected_mpf = round(min(max(customs_value * 0.003464, 31.67), 614.35), 2)
        assert data["fees"]["mpf_usd"] == expected_mpf
        assert data["landed_cost_usd"] == round(customs_value + expected_total_duty + data["total_fees_usd"], 2)

    @pytest.mark.asyncio
    async def test_tariff_breakdown_has_rule_ids(self, client: AsyncClient):
        """Scenario 14: Tariff items (not fees) should reference rule IDs for audit."""
        response = await client.post("/calculate", json={
            "hts_code": "8483.40",
            "invoice_value_usd": 5000,
            "origin_country": "CN",
            "import_date": "2020-01-01",
            "freight_usd": 200,
            "insurance_usd": 10,
        })
        assert response.status_code == 200
        data = response.json()

        for item in data["tariff_breakdown"]:
            # MPF and HMF are fees, not rule-based — no rule_id expected
            if item["applied"] and item["type"] not in ("MPF", "HMF"):
                assert item["rule_id"] is not None

    @pytest.mark.asyncio
    async def test_zero_freight_insurance(self, client: AsyncClient):
        """Scenario 15: Zero freight/insurance — customs value equals invoice."""
        response = await client.post("/calculate", json={
            "hts_code": "8483.40",
            "invoice_value_usd": 10000,
            "origin_country": "CN",
            "import_date": "2020-01-01",
            "freight_usd": 0,
            "insurance_usd": 0,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["customs_value_usd"] == 10000

    @pytest.mark.asyncio
    async def test_calculation_creates_audit_log(self, client: AsyncClient):
        """Scenario 16: Each calculation should create an audit trail entry."""
        # Perform a calculation
        calc_response = await client.post("/calculate", json={
            "hts_code": "8483.40",
            "invoice_value_usd": 5000,
            "origin_country": "CN",
            "import_date": "2020-01-01",
            "freight_usd": 200,
            "insurance_usd": 10,
        })
        assert calc_response.status_code == 200
        calc_id = calc_response.json()["calculation_id"]

        # Query audit trail
        audit_response = await client.get(f"/calculations/{calc_id}")
        assert audit_response.status_code == 200
        audit = audit_response.json()
        assert audit["hts_code"] == "8483.40"
        assert len(audit["matched_rules"]) > 0


class TestHealthEndpoint:
    """Basic health check tests."""

    @pytest.mark.asyncio
    async def test_health(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
