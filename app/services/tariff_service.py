from datetime import date

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tariff_rule import TariffRule
from app.models.exclusion import Exclusion
from app.schemas.tariff import (
    TariffRuleCreate,
    TariffRuleUpdate,
    ExclusionCreate,
    ExclusionUpdate,
    CloseRequest,
)


class TariffService:
    """Service for managing tariff rules and exclusions."""

    VALID_TARIFF_TYPES = {"MFN", "SECTION_301", "SECTION_232", "IEEPA", "AD_CVD"}

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_rules(self, tariff_type: str | None, hts_code: str | None) -> list[TariffRule]:
        stmt = select(TariffRule)
        if tariff_type:
            stmt = stmt.where(TariffRule.tariff_type == tariff_type)
        if hts_code:
            stmt = stmt.where(TariffRule.hts_code_pattern == hts_code)
        stmt = stmt.order_by(TariffRule.tariff_type, TariffRule.effective_from)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_rule(self, data: TariffRuleCreate) -> TariffRule:
        if data.tariff_type not in self.VALID_TARIFF_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid tariff_type. Must be one of: {self.VALID_TARIFF_TYPES}",
            )
        rule = TariffRule(
            tariff_type=data.tariff_type,
            hts_code_pattern=data.hts_code_pattern,
            origin_country=data.origin_country,
            rate=data.rate,
            effective_from=data.effective_from,
            effective_to=data.effective_to,
            stacks_with=data.stacks_with,
            mutually_exclusive_with=data.mutually_exclusive_with,
            description=data.description,
            source_reference=data.source_reference,
        )
        self.db.add(rule)
        await self.db.flush()
        return rule

    async def update_rule(self, rule_id: str, data: TariffRuleUpdate) -> TariffRule:
        stmt = select(TariffRule).where(TariffRule.id == rule_id)
        result = await self.db.execute(stmt)
        rule = result.scalar_one_or_none()
        if not rule:
            raise HTTPException(status_code=404, detail=f"Tariff rule '{rule_id}' not found")

        if data.rate is not None:
            rule.rate = data.rate
        if data.effective_to is not None:
            rule.effective_to = data.effective_to
        if data.stacks_with is not None:
            rule.stacks_with = data.stacks_with
        if data.mutually_exclusive_with is not None:
            rule.mutually_exclusive_with = data.mutually_exclusive_with
        if data.description is not None:
            rule.description = data.description
        if data.source_reference is not None:
            rule.source_reference = data.source_reference

        await self.db.flush()
        return rule

    async def delete_rule(self, rule_id: str) -> None:
        """Hard-delete a tariff rule.

        Guarded: only rules that have **not yet taken effect** (effective_from
        is in the future) may be hard-deleted.  Rules that are currently active
        or have been active in the past must be **closed** via
        ``close_rule()`` instead, preserving the audit trail.
        """
        stmt = select(TariffRule).where(TariffRule.id == rule_id)
        result = await self.db.execute(stmt)
        rule = result.scalar_one_or_none()
        if not rule:
            raise HTTPException(status_code=404, detail=f"Tariff rule '{rule_id}' not found")

        today = date.today()
        if rule.effective_from <= today:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Tariff rule '{rule_id}' has already taken effect "
                    f"(effective_from={rule.effective_from}). "
                    "Use POST /tariff-rules/{id}/close to set an end date instead of deleting. "
                    "This preserves the audit trail for past calculations."
                ),
            )

        await self.db.delete(rule)
        await self.db.flush()

    async def close_rule(self, rule_id: str, data: CloseRequest) -> TariffRule:
        """Soft-close a tariff rule by setting its effective_to date.

        This is the preferred way to "retire" a rule while keeping it in the
        database for audit purposes.  Past calculations that referenced this
        rule are unaffected because their logs store the rules used at calc time.
        """
        stmt = select(TariffRule).where(TariffRule.id == rule_id)
        result = await self.db.execute(stmt)
        rule = result.scalar_one_or_none()
        if not rule:
            raise HTTPException(status_code=404, detail=f"Tariff rule '{rule_id}' not found")

        if rule.effective_to is not None and rule.effective_to <= data.close_date:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Rule already ends on {rule.effective_to}, which is on or before "
                    f"the requested close date {data.close_date}."
                ),
            )

        rule.effective_to = data.close_date
        await self.db.flush()
        return rule

    async def list_exclusions(self, hts_code: str | None) -> list[Exclusion]:
        stmt = select(Exclusion)
        if hts_code:
            stmt = stmt.where(Exclusion.hts_code == hts_code)
        stmt = stmt.order_by(Exclusion.effective_from)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_exclusion(self, data: ExclusionCreate) -> Exclusion:
        if data.tariff_type not in self.VALID_TARIFF_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid tariff_type. Must be one of: {self.VALID_TARIFF_TYPES}",
            )
        exclusion = Exclusion(
            hts_code=data.hts_code,
            tariff_type=data.tariff_type,
            origin_country=data.origin_country,
            effective_from=data.effective_from,
            effective_to=data.effective_to,
            description=data.description,
            source_reference=data.source_reference,
        )
        self.db.add(exclusion)
        await self.db.flush()
        return exclusion

    async def update_exclusion(self, exclusion_id: str, data: ExclusionUpdate) -> Exclusion:
        """Update an exclusion. Raises 404 if not found."""
        stmt = select(Exclusion).where(Exclusion.id == exclusion_id)
        result = await self.db.execute(stmt)
        exclusion = result.scalar_one_or_none()
        if not exclusion:
            raise HTTPException(status_code=404, detail=f"Exclusion '{exclusion_id}' not found")

        if data.effective_to is not None:
            exclusion.effective_to = data.effective_to
        if data.description is not None:
            exclusion.description = data.description
        if data.source_reference is not None:
            exclusion.source_reference = data.source_reference

        await self.db.flush()
        return exclusion

    async def delete_exclusion(self, exclusion_id: str) -> None:
        """Hard-delete an exclusion.

        Guarded: only exclusions that have **not yet taken effect** may be
        hard-deleted.  Active or past exclusions must be **closed** via
        ``close_exclusion()`` to preserve the audit trail.
        """
        stmt = select(Exclusion).where(Exclusion.id == exclusion_id)
        result = await self.db.execute(stmt)
        exclusion = result.scalar_one_or_none()
        if not exclusion:
            raise HTTPException(status_code=404, detail=f"Exclusion '{exclusion_id}' not found")

        today = date.today()
        if exclusion.effective_from <= today:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Exclusion '{exclusion_id}' has already taken effect "
                    f"(effective_from={exclusion.effective_from}). "
                    "Use POST /exclusions/{id}/close to set an end date instead of deleting. "
                    "This preserves the audit trail for past calculations."
                ),
            )

        await self.db.delete(exclusion)
        await self.db.flush()

    async def close_exclusion(self, exclusion_id: str, data: CloseRequest) -> Exclusion:
        """Soft-close an exclusion by setting its effective_to date."""
        stmt = select(Exclusion).where(Exclusion.id == exclusion_id)
        result = await self.db.execute(stmt)
        exclusion = result.scalar_one_or_none()
        if not exclusion:
            raise HTTPException(status_code=404, detail=f"Exclusion '{exclusion_id}' not found")

        if exclusion.effective_to is not None and exclusion.effective_to <= data.close_date:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Exclusion already ends on {exclusion.effective_to}, which is on or before "
                    f"the requested close date {data.close_date}."
                ),
            )

        exclusion.effective_to = data.close_date
        await self.db.flush()
        return exclusion
