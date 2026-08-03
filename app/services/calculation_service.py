"""
Landed Cost Calculation Service.

Orchestrates the full calculation:
1. Validate inputs (HTS code exists, currency conversion available)
2. Convert currency if needed (CNY → USD)
3. Calculate customs value (CIF: Cost + Insurance + Freight)
4. Resolve applicable tariff rules via the Rule Engine
5. Calculate each tariff layer
6. Sum up the landed cost
7. Log the calculation for audit trail
"""

import uuid
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calculation_log import CalculationLog
from app.schemas.calculation import (
    CalculationRequest,
    CalculationResponse,
    TariffBreakdownItem,
    ExclusionApplied,
    FXRateUsed,
)
from app.services.fx_service import FXService
from app.services.hts_service import HTSService
from app.services.rule_engine import RuleEngine


class CalculationService:
    """Orchestrates the landed cost calculation."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.fx_service = FXService(db)
        self.hts_service = HTSService(db)
        self.rule_engine = RuleEngine(db)

    async def calculate(self, request: CalculationRequest) -> CalculationResponse:
        """Perform a full landed cost calculation."""

        # Step 1: Validate HTS code
        hts_exists = await self.hts_service.validate_code_exists(request.hts_code)
        if not hts_exists:
            raise HTTPException(
                status_code=400,
                detail=f"HTS code '{request.hts_code}' not found in the system. Please verify the code.",
            )

        # Step 2: Determine invoice value in USD
        fx_rate_used = None
        if request.invoice_value_cny is not None:
            fx_rate = await self.fx_service.get_rate("CNY", "USD", request.import_date)
            invoice_value_usd = round(request.invoice_value_cny * fx_rate.rate, 2)
            fx_rate_used = FXRateUsed(
                from_currency="CNY",
                to_currency="USD",
                rate=fx_rate.rate,
                fx_date=fx_rate.date,
            )
        elif request.invoice_value_usd is not None:
            invoice_value_usd = request.invoice_value_usd
        else:
            raise HTTPException(
                status_code=400,
                detail="Either invoice_value_cny or invoice_value_usd must be provided",
            )

        # Step 3: Calculate customs value (CIF)
        customs_value_usd = round(invoice_value_usd + request.freight_usd + request.insurance_usd, 2)

        # Step 4: Resolve tariff rules
        resolution = await self.rule_engine.resolve_rules(
            hts_code=request.hts_code,
            origin_country=request.origin_country,
            import_date=request.import_date,
        )

        # Step 5: Calculate each tariff layer
        tariff_breakdown = []
        total_duty = 0.0

        for rule in resolution.applied_rules:
            duty_amount = round(customs_value_usd * rule.rate, 2)
            total_duty += duty_amount
            tariff_breakdown.append(
                TariffBreakdownItem(
                    type=rule.tariff_type,
                    rate=rule.rate,
                    amount_usd=duty_amount,
                    applied=True,
                    rule_id=rule.rule_id,
                )
            )

        # Add excluded rules to breakdown (for transparency)
        for rule, reason in resolution.excluded_rules:
            tariff_breakdown.append(
                TariffBreakdownItem(
                    type=rule.tariff_type,
                    rate=rule.rate,
                    amount_usd=0,
                    applied=False,
                    reason=reason,
                    rule_id=rule.rule_id,
                )
            )

        total_duty = round(total_duty, 2)

        # Step 6: Calculate landed cost
        landed_cost_usd = round(customs_value_usd + total_duty, 2)

        # Step 7: Build exclusions applied list
        exclusions_applied = [
            ExclusionApplied(
                exclusion_id=exc.id,
                tariff_type=exc.tariff_type,
                description=exc.description,
            )
            for exc in resolution.exclusions_used
        ]

        # Step 8: Create audit log
        calculation_id = str(uuid.uuid4())
        log = CalculationLog(
            id=calculation_id,
            hts_code=request.hts_code,
            import_date=request.import_date,
            origin_country=request.origin_country,
            input_data=request.model_dump(mode="json"),
            matched_rules=[r.rule_id for r in resolution.applied_rules],
            exclusions_applied=[exc.id for exc in resolution.exclusions_used],
            result_data={
                "invoice_value_usd": invoice_value_usd,
                "customs_value_usd": customs_value_usd,
                "total_duty_usd": total_duty,
                "landed_cost_usd": landed_cost_usd,
            },
            calculated_at=datetime.now(tz=None),
        )
        self.db.add(log)
        await self.db.flush()

        return CalculationResponse(
            calculation_id=calculation_id,
            hts_code=request.hts_code,
            import_date=request.import_date,
            origin_country=request.origin_country,
            invoice_value_usd=invoice_value_usd,
            customs_value_usd=customs_value_usd,
            total_duty_usd=total_duty,
            landed_cost_usd=landed_cost_usd,
            tariff_breakdown=tariff_breakdown,
            exclusions_applied=exclusions_applied,
            fx_rate_used=fx_rate_used,
        )
