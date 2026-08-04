"""
Database initialization and seeding script.

Usage:
    python -m app.init_db

This creates all tables and loads seed data from real US tariff sources.
"""

import asyncio
import sys

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.database import Base
from app.config import get_settings
from app.models import HTSCode, TariffRule, Exclusion, FXRate
from app.seed_data import HTS_CODES, TARIFF_RULES, EXCLUSIONS, FX_RATES


async def init_database(database_url: str | None = None):
    """Create all tables and seed initial data."""
    url = database_url or get_settings().async_database_url
    engine = create_async_engine(url, echo=True)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Tables created successfully.")

    # Seed data
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        async with session.begin():
            from sqlalchemy import select, func

            # Check if HTS codes need seeding — add any new ones
            result = await session.execute(select(func.count()).select_from(HTSCode))
            hts_count = result.scalar()
            if hts_count == 0:
                for data in HTS_CODES:
                    hts = HTSCode(
                        code=data["code"],
                        level=_determine_level(data["code"]),
                        description=data["description"],
                        parent_code=data["parent_code"],
                    )
                    session.add(hts)
                print(f"Seeded {len(HTS_CODES)} HTS codes.")
            elif hts_count < len(HTS_CODES):
                # Add missing HTS codes
                existing_codes_result = await session.execute(select(HTSCode.code))
                existing_codes = {r[0] for r in existing_codes_result.all()}
                added = 0
                for data in HTS_CODES:
                    if data["code"] not in existing_codes:
                        hts = HTSCode(
                            code=data["code"],
                            level=_determine_level(data["code"]),
                            description=data["description"],
                            parent_code=data["parent_code"],
                        )
                        session.add(hts)
                        added += 1
                print(f"Added {added} new HTS codes (total now: {hts_count + added}).")
            else:
                print(f"HTS codes up to date ({hts_count}).")

            # Always check tariff rules — add any new ones (by checking count)
            result = await session.execute(select(func.count()).select_from(TariffRule))
            rule_count = result.scalar()
            expected_rules = len(TARIFF_RULES)
            if rule_count < expected_rules:
                # Get existing rule descriptions to avoid duplicates
                existing = await session.execute(select(TariffRule.hts_code_pattern, TariffRule.origin_country, TariffRule.tariff_type))
                existing_keys = {(r[0], r[1], r[2]) for r in existing.all()}

                added = 0
                for data in TARIFF_RULES:
                    key = (data["hts_code_pattern"], data["origin_country"], data["tariff_type"])
                    if key not in existing_keys:
                        rule = TariffRule(**data)
                        session.add(rule)
                        added += 1
                print(f"Added {added} new tariff rules (total now: {rule_count + added}).")
            else:
                print(f"Tariff rules up to date ({rule_count}).")

            # Seed exclusions if empty
            result = await session.execute(select(func.count()).select_from(Exclusion))
            if result.scalar() == 0:
                for data in EXCLUSIONS:
                    exclusion = Exclusion(**data)
                    session.add(exclusion)
                print(f"Seeded {len(EXCLUSIONS)} exclusions.")

            # Seed FX rates if empty
            result = await session.execute(select(func.count()).select_from(FXRate))
            if result.scalar() == 0:
                for data in FX_RATES:
                    rate = FXRate(**data)
                    session.add(rate)
                print(f"Seeded {len(FX_RATES)} FX rates.")

    await engine.dispose()
    print("Database initialization complete!")


def _determine_level(code: str) -> str:
    """Determine HTS level from code format."""
    clean = code.replace(".", "")
    if len(clean) <= 2:
        return "chapter"
    elif len(clean) <= 4:
        return "heading"
    else:
        return "subheading"


if __name__ == "__main__":
    # Allow overriding DB URL via command line arg
    url = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(init_database(url))
