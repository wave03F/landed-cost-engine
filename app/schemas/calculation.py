from datetime import date as date_type
from pydantic import BaseModel, Field


class CalculationRequest(BaseModel):
    """Input for landed cost calculation."""

    hts_code: str = Field(..., description="HTS code of the product (e.g. '8483.40')")
    invoice_value_cny: float | None = Field(default=None, description="Invoice value in CNY")
    invoice_value_usd: float | None = Field(default=None, description="Invoice value in USD (use if already in USD)")
    origin_country: str = Field(default="CN", description="ISO 2-letter origin country code")
    import_date: date_type = Field(..., description="Date of import (determines which rules apply)")
    freight_usd: float = Field(default=0, ge=0, description="Freight cost in USD")
    insurance_usd: float = Field(default=0, ge=0, description="Insurance cost in USD")

    model_config = {"json_schema_extra": {"examples": [{"hts_code": "8483.40", "invoice_value_cny": 50000, "origin_country": "CN", "import_date": "2026-08-01", "freight_usd": 800, "insurance_usd": 50}]}}


class TariffBreakdownItem(BaseModel):
    """One layer of tariff in the breakdown."""

    type: str = Field(..., description="Tariff type (MFN, SECTION_301, SECTION_232, IEEPA)")
    rate: float | None = Field(default=None, description="Applied rate")
    amount_usd: float | None = Field(default=None, description="Tariff amount in USD")
    applied: bool = Field(default=True, description="Whether this tariff was actually applied")
    reason: str | None = Field(default=None, description="Reason if not applied (e.g. exclusion, stacking rule)")
    rule_id: str | None = Field(default=None, description="Reference to the tariff rule used")


class ExclusionApplied(BaseModel):
    """An exclusion that was applied during calculation."""

    exclusion_id: str
    tariff_type: str
    description: str


class FXRateUsed(BaseModel):
    """FX rate details used in the calculation."""

    from_currency: str
    to_currency: str
    rate: float
    fx_date: date_type = Field(serialization_alias="date")


class CalculationResponse(BaseModel):
    """Full landed cost calculation result with audit trail."""

    calculation_id: str = Field(..., description="Unique ID for this calculation (for audit)")
    hts_code: str
    import_date: date_type
    origin_country: str
    invoice_value_usd: float = Field(..., description="Invoice value converted to USD")
    customs_value_usd: float = Field(..., description="CIF value (invoice + freight + insurance) in USD")
    total_duty_usd: float = Field(..., description="Total duty amount across all applicable tariff layers")
    landed_cost_usd: float = Field(..., description="Final landed cost (customs value + total duty)")
    tariff_breakdown: list[TariffBreakdownItem] = Field(..., description="Detail of each tariff layer")
    exclusions_applied: list[ExclusionApplied] = Field(default_factory=list)
    fx_rate_used: FXRateUsed | None = Field(default=None, description="FX rate used if currency conversion was needed")

    model_config = {"populate_by_name": True}
