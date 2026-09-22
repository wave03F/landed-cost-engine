from datetime import date
from pydantic import BaseModel, Field


class TariffRuleCreate(BaseModel):
    tariff_type: str = Field(..., description="Type: MFN, SECTION_301, SECTION_232, IEEPA")
    hts_code_pattern: str = Field(..., description="HTS code or prefix pattern (e.g. '84' matches all chapter 84)")
    origin_country: str = Field(default="CN", description="ISO 2-letter country code")
    rate: float = Field(..., ge=0, le=5.0, description="Tariff rate as decimal (e.g. 0.25 = 25%)")
    effective_from: date = Field(..., description="Date the rule takes effect")
    effective_to: date | None = Field(default=None, description="Date the rule expires (null = still active)")
    stacks_with: list[str] = Field(default_factory=list, description="Tariff types this rule stacks with")
    mutually_exclusive_with: list[str] = Field(default_factory=list, description="Tariff types where only the higher rate applies")
    description: str = Field(default="", description="Human-readable description of the rule")
    source_reference: str = Field(default="", description="Legal/regulatory reference")

    model_config = {"json_schema_extra": {"examples": [{"tariff_type": "SECTION_301", "hts_code_pattern": "84", "origin_country": "CN", "rate": 0.25, "effective_from": "2018-07-06", "effective_to": None, "stacks_with": ["MFN"], "mutually_exclusive_with": ["IEEPA"], "description": "Section 301 List 1 - 25% tariff on Chinese goods", "source_reference": "USTR FR Notice 83 FR 28710"}]}}


class TariffRuleUpdate(BaseModel):
    rate: float | None = Field(default=None, ge=0, le=5.0)
    effective_to: date | None = None
    stacks_with: list[str] | None = None
    mutually_exclusive_with: list[str] | None = None
    description: str | None = None
    source_reference: str | None = None


class TariffRuleResponse(BaseModel):
    id: str
    tariff_type: str
    hts_code_pattern: str
    origin_country: str
    rate: float
    effective_from: date
    effective_to: date | None
    stacks_with: list[str]
    mutually_exclusive_with: list[str]
    description: str
    source_reference: str

    model_config = {"from_attributes": True}


class ExclusionCreate(BaseModel):
    hts_code: str = Field(..., description="Specific HTS code excluded")
    tariff_type: str = Field(..., description="Tariff type being excluded (e.g. SECTION_301)")
    origin_country: str = Field(default="CN")
    effective_from: date = Field(...)
    effective_to: date | None = Field(default=None)
    description: str = Field(default="")
    source_reference: str = Field(default="")


class ExclusionUpdate(BaseModel):
    effective_to: date | None = None
    description: str | None = None
    source_reference: str | None = None


class ExclusionResponse(BaseModel):
    id: str
    hts_code: str
    tariff_type: str
    origin_country: str
    effective_from: date
    effective_to: date | None
    description: str
    source_reference: str

    model_config = {"from_attributes": True}
