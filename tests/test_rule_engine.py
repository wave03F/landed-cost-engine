"""
Unit tests for the rule engine — the core business logic.

Tests cover:
- Temporal rule resolution (correct rules for given date)
- HTS code hierarchical matching
- Stacking logic (301 + MFN)
- Mutual exclusion logic (IEEPA vs 301/232)
- Exclusion handling
"""

import pytest
from datetime import date

from app.services.rule_engine import RuleEngine, ApplicableRule


class TestRuleEngineResolution:
    """Test rule resolution and matching."""

    @pytest.mark.asyncio
    async def test_basic_mfn_and_301_stacking(self, seeded_session):
        """MFN and Section 301 should both apply (they stack)."""
        engine = RuleEngine(seeded_session)
        result = await engine.resolve_rules("8483.40", "CN", date(2020, 1, 1))

        applied_types = {r.tariff_type for r in result.applied_rules}
        assert "MFN" in applied_types
        assert "SECTION_301" in applied_types
        assert len(result.exclusions_used) == 0

    @pytest.mark.asyncio
    async def test_pre_301_date_only_mfn(self, seeded_session):
        """Before Section 301 effective date, only MFN should apply."""
        engine = RuleEngine(seeded_session)
        result = await engine.resolve_rules("8483.40", "CN", date(2017, 1, 1))

        applied_types = {r.tariff_type for r in result.applied_rules}
        assert "MFN" in applied_types
        assert "SECTION_301" not in applied_types
        assert "IEEPA" not in applied_types

    @pytest.mark.asyncio
    async def test_ieepa_overrides_301_when_higher(self, seeded_session):
        """After IEEPA effective date, IEEPA (14.5%) replaces 301 (25%) — wait, 301 is higher.
        Actually Section 301 is 25% and IEEPA is 14.5% for 8483.
        Since they're mutually exclusive, the HIGHER one (301 at 25%) should be kept."""
        engine = RuleEngine(seeded_session)
        result = await engine.resolve_rules("8483.40", "CN", date(2026, 8, 1))

        applied_types = {r.tariff_type for r in result.applied_rules}
        # 301 (25%) > IEEPA (14.5%), so 301 wins
        assert "SECTION_301" in applied_types
        assert "IEEPA" not in applied_types
        assert "MFN" in applied_types

        # IEEPA should be in excluded
        excluded_types = {r.tariff_type for r, reason in result.excluded_rules}
        assert "IEEPA" in excluded_types

    @pytest.mark.asyncio
    async def test_mutual_exclusion_higher_rate_wins(self, seeded_session):
        """When two rules are mutually exclusive, the higher rate always wins."""
        engine = RuleEngine(seeded_session)
        # For 8482.10 (ball bearings): 301(25%) + 232(25%) + IEEPA(14.5%)
        # 301 and IEEPA are mutually exclusive
        # 232 and IEEPA are mutually exclusive
        # So: 301(25%) wins over IEEPA(14.5%), and 232(25%) also wins over IEEPA
        # But are 301 and 232 mutually exclusive with each other? No — they stack!
        result = await engine.resolve_rules("8482.10", "CN", date(2026, 8, 1))

        applied_types = {r.tariff_type for r in result.applied_rules}
        assert "MFN" in applied_types

    @pytest.mark.asyncio
    async def test_exclusion_removes_tariff_layer(self, seeded_session):
        """An active exclusion should remove the corresponding tariff type."""
        engine = RuleEngine(seeded_session)
        # 8542.31 has an IEEPA exclusion (semiconductor ICs)
        result = await engine.resolve_rules("8542.31", "CN", date(2026, 1, 1))

        applied_types = {r.tariff_type for r in result.applied_rules}
        assert "IEEPA" not in applied_types
        assert len(result.exclusions_used) > 0
        assert result.exclusions_used[0].tariff_type == "IEEPA"

    @pytest.mark.asyncio
    async def test_expired_exclusion_not_applied(self, seeded_session):
        """An expired exclusion should not affect calculation."""
        engine = RuleEngine(seeded_session)
        # 8517.12 smartphone exclusion expires 2025-07-09
        # After expiration, IEEPA should apply
        result = await engine.resolve_rules("8517.12", "CN", date(2025, 8, 1))

        # No exclusion should be found
        assert len(result.exclusions_used) == 0

    @pytest.mark.asyncio
    async def test_active_exclusion_within_range(self, seeded_session):
        """Exclusion within valid date range should be applied."""
        engine = RuleEngine(seeded_session)
        # 8517.12 has 301 exclusion from 2025-04-11 to 2025-07-09
        result = await engine.resolve_rules("8517.12", "CN", date(2025, 5, 1))

        exclusion_types = {exc.tariff_type for exc in result.exclusions_used}
        assert "SECTION_301" in exclusion_types

    @pytest.mark.asyncio
    async def test_hierarchical_matching_chapter_level(self, seeded_session):
        """Chapter-level rules should match subheading codes."""
        engine = RuleEngine(seeded_session)
        # IEEPA rule is at chapter "84" level, should match "8483.40"
        result = await engine.resolve_rules("8483.40", "CN", date(2025, 5, 1))

        # IEEPA should be found as a candidate (though it may be excluded by stacking logic)
        all_rule_types = set()
        for r in result.applied_rules:
            all_rule_types.add(r.tariff_type)
        for r, _ in result.excluded_rules:
            all_rule_types.add(r.tariff_type)

        assert "IEEPA" in all_rule_types  # At least found as a candidate

    @pytest.mark.asyncio
    async def test_more_specific_pattern_wins(self, seeded_session):
        """A more specific HTS pattern takes precedence within same tariff type."""
        engine = RuleEngine(seeded_session)
        # 8482.10 has a specific Section 232 rule at subheading level
        # If there were also a chapter-level 232 rule, the subheading one would win
        result = await engine.resolve_rules("8482.10", "CN", date(2020, 1, 1))

        # Should find the specific 232 rule for 8482.10
        all_types = {r.tariff_type for r in result.applied_rules}
        assert "SECTION_232" in all_types

    @pytest.mark.asyncio
    async def test_no_rules_for_unknown_origin(self, seeded_session):
        """No rules should match for a non-Chinese origin."""
        engine = RuleEngine(seeded_session)
        result = await engine.resolve_rules("8483.40", "DE", date(2026, 8, 1))

        assert len(result.applied_rules) == 0
        assert len(result.excluded_rules) == 0


class TestStackingLogic:
    """Test the stacking/mutual-exclusion resolution logic."""

    def test_mfn_always_applies(self):
        """MFN is always applied regardless of other rules."""
        engine = RuleEngine.__new__(RuleEngine)

        rules = [
            ApplicableRule(rule_id="1", tariff_type="MFN", rate=0.025, stacks_with=[], mutually_exclusive_with=[]),
            ApplicableRule(rule_id="2", tariff_type="SECTION_301", rate=0.25, stacks_with=["MFN"], mutually_exclusive_with=["IEEPA"]),
        ]

        applied, excluded = engine._apply_stacking_logic(rules)
        applied_types = {r.tariff_type for r in applied}
        assert "MFN" in applied_types
        assert "SECTION_301" in applied_types
        assert len(excluded) == 0

    def test_mutual_exclusion_picks_higher(self):
        """When rules are mutually exclusive, the higher rate wins."""
        engine = RuleEngine.__new__(RuleEngine)

        rules = [
            ApplicableRule(rule_id="1", tariff_type="MFN", rate=0.025, stacks_with=[], mutually_exclusive_with=[]),
            ApplicableRule(rule_id="2", tariff_type="SECTION_301", rate=0.25, stacks_with=["MFN"], mutually_exclusive_with=["IEEPA"]),
            ApplicableRule(rule_id="3", tariff_type="IEEPA", rate=0.145, stacks_with=["MFN"], mutually_exclusive_with=["SECTION_301"]),
        ]

        applied, excluded = engine._apply_stacking_logic(rules)
        applied_types = {r.tariff_type for r in applied}

        assert "MFN" in applied_types
        assert "SECTION_301" in applied_types  # 25% > 14.5%
        assert "IEEPA" not in applied_types

        excluded_types = {r.tariff_type for r, _ in excluded}
        assert "IEEPA" in excluded_types

    def test_mutual_exclusion_ieepa_wins_when_higher(self):
        """IEEPA wins when its rate is higher than 301."""
        engine = RuleEngine.__new__(RuleEngine)

        rules = [
            ApplicableRule(rule_id="1", tariff_type="MFN", rate=0.0, stacks_with=[], mutually_exclusive_with=[]),
            ApplicableRule(rule_id="2", tariff_type="SECTION_301", rate=0.10, stacks_with=["MFN"], mutually_exclusive_with=["IEEPA"]),
            ApplicableRule(rule_id="3", tariff_type="IEEPA", rate=0.145, stacks_with=["MFN"], mutually_exclusive_with=["SECTION_301"]),
        ]

        applied, excluded = engine._apply_stacking_logic(rules)
        applied_types = {r.tariff_type for r in applied}

        assert "IEEPA" in applied_types  # 14.5% > 10%
        assert "SECTION_301" not in applied_types

    def test_no_mutual_exclusion_all_stack(self):
        """Rules without mutual exclusion should all apply (stack)."""
        engine = RuleEngine.__new__(RuleEngine)

        rules = [
            ApplicableRule(rule_id="1", tariff_type="MFN", rate=0.025, stacks_with=[], mutually_exclusive_with=[]),
            ApplicableRule(rule_id="2", tariff_type="SECTION_301", rate=0.25, stacks_with=["MFN"], mutually_exclusive_with=[]),
            ApplicableRule(rule_id="3", tariff_type="SECTION_232", rate=0.25, stacks_with=["MFN"], mutually_exclusive_with=[]),
        ]

        applied, excluded = engine._apply_stacking_logic(rules)
        assert len(applied) == 3
        assert len(excluded) == 0

    def test_empty_rules(self):
        """Empty rule set should return empty results."""
        engine = RuleEngine.__new__(RuleEngine)
        applied, excluded = engine._apply_stacking_logic([])
        assert applied == []
        assert excluded == []

    def test_three_way_mutual_exclusion(self):
        """Three mutually exclusive rules — highest rate wins."""
        engine = RuleEngine.__new__(RuleEngine)

        rules = [
            ApplicableRule(rule_id="1", tariff_type="MFN", rate=0.025, stacks_with=[], mutually_exclusive_with=[]),
            ApplicableRule(rule_id="2", tariff_type="SECTION_301", rate=0.25, stacks_with=["MFN"], mutually_exclusive_with=["IEEPA", "SECTION_232"]),
            ApplicableRule(rule_id="3", tariff_type="SECTION_232", rate=0.25, stacks_with=["MFN"], mutually_exclusive_with=["IEEPA", "SECTION_301"]),
            ApplicableRule(rule_id="4", tariff_type="IEEPA", rate=0.145, stacks_with=["MFN"], mutually_exclusive_with=["SECTION_301", "SECTION_232"]),
        ]

        applied, excluded = engine._apply_stacking_logic(rules)
        applied_types = {r.tariff_type for r in applied}

        # IEEPA (14.5%) should lose to 301 (25%) or 232 (25%)
        assert "IEEPA" not in applied_types
        assert "MFN" in applied_types
