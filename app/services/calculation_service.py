"""
Landed Cost Calculation Service.

Full real-world calculation pipeline:
1. Validate inputs (HTS code exists)
2. Convert currency if needed (CNY → USD) — DB or live API
3. Check De minimis ($800 threshold)
4. Calculate customs value (CIF: Cost + Insurance + Freight)
5. Check FTA eligibility (USMCA for MX/CA)
6. Resolve applicable tariff rules via the Rule Engine
7. Calculate each tariff layer (MFN, 301, 232, IEEPA, AD/CVD)
8. Calculate fees (MPF + HMF)
9. Sum up the landed cost
10. Log the calculation for audit trail
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
    FeeBreakdown,
)
from app.services.fx_service import FXService
from app.services.hts_service import HTSService
from app.services.rule_engine import RuleEngine


# =============================================================================
# Constants — US Customs fees
# =============================================================================

# Merchandise Processing Fee (MPF): 19 CFR 24.23
MPF_RATE = 0.003464  # 0.3464%
MPF_MIN = 31.67  # Minimum per entry
MPF_MAX = 614.35  # Maximum per entry

# Harbor Maintenance Fee (HMF): 19 USC 58c
HMF_RATE = 0.00125  # 0.125%

# De minimis threshold: 19 USC 1321
DE_MINIMIS_THRESHOLD = 800.0  # USD

# Free Trade Agreements — countries that get MFN exemption for qualifying goods
FTA_AGREEMENTS: dict[str, dict] = {
    "MX": {"name": "USMCA", "exempts_mfn": True},
    "CA": {"name": "USMCA", "exempts_mfn": True},
}


class CalculationService:
    """Orchestrates the full landed cost calculation."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.fx_service = FXService(db)
        self.hts_service = HTSService(db)
        self.rule_engine = RuleEngine(db)

    async def calculate(self, request: CalculationRequest) -> CalculationResponse:
        """Perform a full landed cost calculation with all real-world rules."""

        # Step 1: Validate HTS code
        hts_exists = await self.hts_service.validate_code_exists(request.hts_code)
        if not hts_exists:
            raise HTTPException(
                status_code=400,
                detail=f"HTS code '{request.hts_code}' not found in the system. Please verify the code.",
            )

        # Step 2: Determine invoice value in USD
        fx_rate_used = None
        fx_source = "database"
        if request.invoice_value_cny is not None:
            fx_rate, fx_source = await self.fx_service.get_rate_with_fallback(
                "CNY", "USD", request.import_date
            )
            invoice_value_usd = round(request.invoice_value_cny * fx_rate.rate, 2)
            fx_rate_used = FXRateUsed(
                from_currency="CNY",
                to_currency="USD",
                rate=fx_rate.rate,
                fx_date=fx_rate.date,
                source=fx_source,
            )
        elif request.invoice_value_usd is not None:
            invoice_value_usd = request.invoice_value_usd
        else:
            raise HTTPException(
                status_code=400,
                detail="Either invoice_value_cny or invoice_value_usd must be provided",
            )

        # Step 3: Check De minimis threshold
        total_value = invoice_value_usd + request.freight_usd + request.insurance_usd
        if total_value <= DE_MINIMIS_THRESHOLD:
            # De minimis: no duties, no fees
            calculation_id = str(uuid.uuid4())
            await self._log_calculation(
                calculation_id, request, invoice_value_usd, total_value, 0, 0, total_value, True
            )
            return CalculationResponse(
                calculation_id=calculation_id,
                hts_code=request.hts_code,
                import_date=request.import_date,
                origin_country=request.origin_country,
                de_minimis_applied=True,
                invoice_value_usd=invoice_value_usd,
                customs_value_usd=total_value,
                total_duty_usd=0,
                tariff_breakdown=[],
                fees=None,
                fta_applied=None,
                total_fees_usd=0,
                landed_cost_usd=total_value,
                exclusions_applied=[],
                fx_rate_used=fx_rate_used,
            )

        # Step 4: Calculate customs value (CIF)
        customs_value_usd = round(total_value, 2)

        # Step 5: Check FTA eligibility
        fta_info = FTA_AGREEMENTS.get(request.origin_country)
        fta_applied = fta_info["name"] if fta_info else None

        # Step 6: Resolve tariff rules
        resolution = await self.rule_engine.resolve_rules(
            hts_code=request.hts_code,
            origin_country=request.origin_country,
            import_date=request.import_date,
        )

        # Step 7: Calculate each tariff layer
        tariff_breakdown = []
        total_duty = 0.0

        for rule in resolution.applied_rules:
            # If FTA applies and this is MFN, set to 0
            if fta_info and fta_info["exempts_mfn"] and rule.tariff_type == "MFN":
                tariff_breakdown.append(
                    TariffBreakdownItem(
                        type=rule.tariff_type,
                        rate=rule.rate,
                        amount_usd=0,
                        applied=False,
                        reason=f"exempt_under_{fta_applied}",
                        rule_id=rule.rule_id,
                    )
                )
                continue

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

        # Step 8: Calculate fees (MPF + HMF)
        mpf = self._calculate_mpf(customs_value_usd)
        hmf = self._calculate_hmf(customs_value_usd)
        total_fees = round(mpf + hmf, 2)

        # Add fees to breakdown for visibility
        tariff_breakdown.append(
            TariffBreakdownItem(type="MPF", rate=MPF_RATE, amount_usd=mpf, applied=True)
        )
        tariff_breakdown.append(
            TariffBreakdownItem(type="HMF", rate=HMF_RATE, amount_usd=hmf, applied=True)
        )

        fees = FeeBreakdown(mpf_usd=mpf, hmf_usd=hmf, total_fees_usd=total_fees)

        # Step 9: Calculate landed cost
        landed_cost_usd = round(customs_value_usd + total_duty + total_fees, 2)

        # Step 10: Build exclusions applied list
        exclusions_applied = [
            ExclusionApplied(
                exclusion_id=exc.id,
                tariff_type=exc.tariff_type,
                description=exc.description,
            )
            for exc in resolution.exclusions_used
        ]

        # Step 11: Create audit log
        calculation_id = str(uuid.uuid4())
        await self._log_calculation(
            calculation_id, request, invoice_value_usd, customs_value_usd,
            total_duty, total_fees, landed_cost_usd, False,
            [r.rule_id for r in resolution.applied_rules],
            [exc.id for exc in resolution.exclusions_used],
        )

        return CalculationResponse(
            calculation_id=calculation_id,
            hts_code=request.hts_code,
            import_date=request.import_date,
            origin_country=request.origin_country,
            de_minimis_applied=False,
            invoice_value_usd=invoice_value_usd,
            customs_value_usd=customs_value_usd,
            total_duty_usd=total_duty,
            tariff_breakdown=tariff_breakdown,
            fees=fees,
            fta_applied=fta_applied,
            total_fees_usd=total_fees,
            landed_cost_usd=landed_cost_usd,
            exclusions_applied=exclusions_applied,
            fx_rate_used=fx_rate_used,
        )

    # =========================================================================
    # Fee calculations
    # =========================================================================

    def _calculate_mpf(self, customs_value: float) -> float:
        """
        Merchandise Processing Fee (MPF).
        Rate: 0.3464% of CIF value
        Min: $31.67 per entry
        Max: $614.35 per entry
        Authority: 19 CFR 24.23
        """
        mpf = customs_value * MPF_RATE
        mpf = max(mpf, MPF_MIN)
        mpf = min(mpf, MPF_MAX)
        return round(mpf, 2)

    def _calculate_hmf(self, customs_value: float) -> float:
        """
        Harbor Maintenance Fee (HMF).
        Rate: 0.125% of CIF value
        No min/max cap.
        Authority: 19 USC 58c
        Applies to all waterborne imports.
        """
        return round(customs_value * HMF_RATE, 2)

    # =========================================================================
    # Audit logging
    # =========================================================================

    async def _log_calculation(
        self,
        calculation_id: str,
        request: CalculationRequest,
        invoice_value_usd: float,
        customs_value_usd: float,
        total_duty: float,
        total_fees: float,
        landed_cost_usd: float,
        de_minimis: bool,
        matched_rules: list[str] | None = None,
        exclusions_applied: list[str] | None = None,
    ):
        log = CalculationLog(
            id=calculation_id,
            hts_code=request.hts_code,
            import_date=request.import_date,
            origin_country=request.origin_country,
            input_data=request.model_dump(mode="json"),
            matched_rules=matched_rules or [],
            exclusions_applied=exclusions_applied or [],
            result_data={
                "invoice_value_usd": invoice_value_usd,
                "customs_value_usd": customs_value_usd,
                "total_duty_usd": total_duty,
                "total_fees_usd": total_fees,
                "landed_cost_usd": landed_cost_usd,
                "de_minimis_applied": de_minimis,
            },
            calculated_at=datetime.now(tz=None),
        )
        self.db.add(log)
        await self.db.flush()
