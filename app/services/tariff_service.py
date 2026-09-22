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
        """Delete a tariff rule. Raises 404 if not found.
        Past calculation logs are unaffected (they store the rule ids used at calc time)."""
        stmt = select(TariffRule).where(TariffRule.id == rule_id)
        result = await self.db.execute(stmt)
        rule = result.scalar_one_or_none()
        if not rule:
            raise HTTPException(status_code=404, detail=f"Tariff rule '{rule_id}' not found")
        await self.db.delete(rule)
        await self.db.flush()

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
        """Delete an exclusion. Raises 404 if not found."""
        stmt = select(Exclusion).where(Exclusion.id == exclusion_id)
        result = await self.db.execute(stmt)
        exclusion = result.scalar_one_or_none()
        if not exclusion:
            raise HTTPException(status_code=404, detail=f"Exclusion '{exclusion_id}' not found")
        await self.db.delete(exclusion)
        await self.db.flush()
