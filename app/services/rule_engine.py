"""
Rule Engine for tariff calculation.

This is the core business logic component. It resolves which tariff rules apply
for a given product on a given date, handles stacking/mutual-exclusion logic,
and checks for exclusions.

Stacking Logic:
- MFN (base rate) always applies as the foundation
- Additional tariffs (301, 232, IEEPA) stack ON TOP of MFN if they list "MFN" in stacks_with
- Mutually exclusive tariffs: only the highest rate applies
  (e.g., if both Section 232 and IEEPA apply to the same product, only the higher one is charged)

Real-world context:
- Section 301: Trade Act of 1974, used for China-specific tariffs (List 1-4)
- Section 232: National security tariffs (steel/aluminum)
- IEEPA: International Emergency Economic Powers Act, used for broad reciprocal tariffs
"""

from datetime import date
from dataclasses import dataclass

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tariff_rule import TariffRule
from app.models.exclusion import Exclusion


@dataclass
class ApplicableRule:
    """A tariff rule that has been resolved as applicable."""
    rule_id: str
    tariff_type: str
    rate: float
    stacks_with: list[str]
    mutually_exclusive_with: list[str]


@dataclass
class RuleResolutionResult:
    """The final set of tariff layers to apply after stacking/exclusion logic."""
    applied_rules: list[ApplicableRule]
    excluded_rules: list[tuple[ApplicableRule, str]]  # (rule, reason)
    exclusions_used: list[Exclusion]


class RuleEngine:
    """
    Resolves applicable tariff rules and applies stacking/exclusion logic.

    Algorithm:
    1. Find all rules matching the HTS code + origin country + date range
    2. Check exclusions — remove any tariff type that has an active exclusion
    3. Apply stacking logic:
       a. Group rules by tariff type (each type should have at most one effective rule)
       b. Identify mutually exclusive groups
       c. Within each exclusive group, keep only the highest rate
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def resolve_rules(
        self,
        hts_code: str,
        origin_country: str,
        import_date: date,
    ) -> RuleResolutionResult:
        """
        Resolve all applicable tariff rules for the given parameters.
        Returns applied rules, excluded rules with reasons, and exclusions used.
        """
        # Step 1: Find matching rules
        matching_rules = await self._find_matching_rules(hts_code, origin_country, import_date)

        # Step 2: Check exclusions
        active_exclusions = await self._find_active_exclusions(hts_code, origin_country, import_date)
        excluded_types = {exc.tariff_type for exc in active_exclusions}

        # Separate excluded rules
        applicable = []
        excluded_by_exclusion = []
        for rule in matching_rules:
            if rule.tariff_type in excluded_types:
                excluded_by_exclusion.append((rule, "excluded_by_tariff_exclusion"))
            else:
                applicable.append(rule)

        # Step 3: Apply stacking/mutual-exclusion logic
        applied, excluded_by_stacking = self._apply_stacking_logic(applicable)

        all_excluded = excluded_by_exclusion + excluded_by_stacking

        return RuleResolutionResult(
            applied_rules=applied,
            excluded_rules=all_excluded,
            exclusions_used=active_exclusions,
        )

    async def _find_matching_rules(
        self,
        hts_code: str,
        origin_country: str,
        import_date: date,
    ) -> list[ApplicableRule]:
        """
        Find all tariff rules that match the given HTS code, origin, and date.

        HTS matching is hierarchical:
        - A rule for "84" matches "8483.40" (chapter-level rule)
        - A rule for "8483" matches "8483.40" (heading-level rule)
        - A rule for "8483.40" matches exactly
        More specific rules take precedence within the same tariff type.
        """
        clean_code = hts_code.replace(".", "")

        # Generate all possible prefix patterns
        prefixes = []
        for i in range(2, len(clean_code) + 1):
            prefix = clean_code[:i]
            prefixes.append(prefix)
            # Also try with dot format
            if len(prefix) > 4:
                prefixes.append(f"{prefix[:4]}.{prefix[4:]}")

        # Also add the original code as-is
        prefixes.append(hts_code)

        # Query rules where hts_code_pattern matches any prefix
        # and is within the effective date range
        stmt = select(TariffRule).where(
            and_(
                TariffRule.hts_code_pattern.in_(prefixes),
                TariffRule.origin_country == origin_country,
                TariffRule.effective_from <= import_date,
                or_(
                    TariffRule.effective_to.is_(None),
                    TariffRule.effective_to >= import_date,
                ),
            )
        )
        result = await self.db.execute(stmt)
        rules = result.scalars().all()

        # For each tariff type, keep only the most specific rule (longest pattern match)
        best_by_type: dict[str, TariffRule] = {}
        for rule in rules:
            existing = best_by_type.get(rule.tariff_type)
            if existing is None or len(rule.hts_code_pattern) > len(existing.hts_code_pattern):
                best_by_type[rule.tariff_type] = rule

        return [
            ApplicableRule(
                rule_id=rule.id,
                tariff_type=rule.tariff_type,
                rate=rule.rate,
                stacks_with=rule.stacks_with or [],
                mutually_exclusive_with=rule.mutually_exclusive_with or [],
            )
            for rule in best_by_type.values()
        ]

    async def _find_active_exclusions(
        self,
        hts_code: str,
        origin_country: str,
        import_date: date,
    ) -> list[Exclusion]:
        """Find all active exclusions for the given HTS code on the import date."""
        stmt = select(Exclusion).where(
            and_(
                Exclusion.hts_code == hts_code,
                Exclusion.origin_country == origin_country,
                Exclusion.effective_from <= import_date,
                or_(
                    Exclusion.effective_to.is_(None),
                    Exclusion.effective_to >= import_date,
                ),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    def _apply_stacking_logic(
        self,
        rules: list[ApplicableRule],
    ) -> tuple[list[ApplicableRule], list[tuple[ApplicableRule, str]]]:
        """
        Apply stacking and mutual-exclusion logic.

        Rules:
        1. MFN always applies (it's the base rate)
        2. Rules that declare stacks_with = ["MFN"] are added on top of MFN
        3. Rules that are mutually_exclusive_with each other — only the highest rate applies

        Returns (applied_rules, excluded_rules_with_reasons)
        """
        if not rules:
            return [], []

        applied = []
        excluded = []

        # Build a map by type for easy lookup
        rules_by_type = {r.tariff_type: r for r in rules}

        # MFN always applies if present
        mfn_rule = rules_by_type.get("MFN")
        if mfn_rule:
            applied.append(mfn_rule)

        # Gather non-MFN rules
        non_mfn_rules = [r for r in rules if r.tariff_type != "MFN"]

        # Identify mutually exclusive groups and resolve
        processed_types = set()

        for rule in non_mfn_rules:
            if rule.tariff_type in processed_types:
                continue

            # Find all rules mutually exclusive with this one
            exclusive_group = [rule]
            for other in non_mfn_rules:
                if other.tariff_type == rule.tariff_type:
                    continue
                if (
                    other.tariff_type in rule.mutually_exclusive_with
                    or rule.tariff_type in other.mutually_exclusive_with
                ):
                    exclusive_group.append(other)

            if len(exclusive_group) > 1:
                # Keep only the highest rate in the group
                exclusive_group.sort(key=lambda r: r.rate, reverse=True)
                winner = exclusive_group[0]
                applied.append(winner)
                processed_types.add(winner.tariff_type)

                for loser in exclusive_group[1:]:
                    excluded.append((loser, "excluded_by_stacking_rule"))
                    processed_types.add(loser.tariff_type)
            else:
                # No mutual exclusion — just apply it (it stacks)
                applied.append(rule)
                processed_types.add(rule.tariff_type)

        return applied, excluded
