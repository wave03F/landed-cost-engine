"""
Unit tests for API Key authentication.

Tests cover:
- Auth disabled when no keys configured (dev mode)
- Valid API key passes
- Missing key returns 401
- Invalid key returns 401
"""

import pytest
from unittest.mock import patch
from httpx import AsyncClient


class TestAuthDisabled:
    """When API_KEYS is empty, auth is disabled (dev mode)."""

    @pytest.mark.asyncio
    async def test_no_key_required_in_dev_mode(self, client: AsyncClient):
        """Without API keys configured, requests work without auth header."""
        response = await client.get("/health")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_calculate_works_without_key(self, client: AsyncClient):
        """Calculation endpoint works in dev mode without key."""
        response = await client.post("/calculate", json={
            "hts_code": "8483.40",
            "invoice_value_usd": 5000,
            "origin_country": "CN",
            "import_date": "2020-01-01",
            "freight_usd": 200,
            "insurance_usd": 10,
        })
        assert response.status_code == 200


class TestAuthEnabled:
    """When API_KEYS has values, auth is enforced."""

    @pytest.mark.asyncio
    async def test_valid_key_passes(self, client: AsyncClient):
        """Request with valid API key should succeed."""
        with patch("app.auth.get_settings") as mock:
            mock.return_value.api_keys = ["test-key-123"]
            response = await client.post(
                "/calculate",
                json={
                    "hts_code": "8483.40",
                    "invoice_value_usd": 5000,
                    "origin_country": "CN",
                    "import_date": "2020-01-01",
                    "freight_usd": 200,
                    "insurance_usd": 10,
                },
                headers={"X-API-Key": "test-key-123"},
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_missing_key_returns_401(self, client: AsyncClient):
        """Request without API key should get 401."""
        with patch("app.auth.get_settings") as mock:
            mock.return_value.api_keys = ["test-key-123"]
            response = await client.post(
                "/calculate",
                json={
                    "hts_code": "8483.40",
                    "invoice_value_usd": 5000,
                    "origin_country": "CN",
                    "import_date": "2020-01-01",
                    "freight_usd": 200,
                    "insurance_usd": 10,
                },
            )
            assert response.status_code == 401
            assert "Missing API key" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_invalid_key_returns_401(self, client: AsyncClient):
        """Request with wrong API key should get 401."""
        with patch("app.auth.get_settings") as mock:
            mock.return_value.api_keys = ["correct-key"]
            response = await client.post(
                "/calculate",
                json={
                    "hts_code": "8483.40",
                    "invoice_value_usd": 5000,
                    "origin_country": "CN",
                    "import_date": "2020-01-01",
                    "freight_usd": 200,
                    "insurance_usd": 10,
                },
                headers={"X-API-Key": "wrong-key"},
            )
            assert response.status_code == 401
            assert "Invalid API key" in response.json()["detail"]


class TestHealthEndpointNoAuth:
    """Health endpoint should never require auth."""

    @pytest.mark.asyncio
    async def test_health_always_accessible(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
