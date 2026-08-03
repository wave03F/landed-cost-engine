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
    url = database_url or get_settings().database_url
    engine = create_async_engine(url, echo=True)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Tables created successfully.")

    # Seed data
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        async with session.begin():
            # Check if data already exists
            from sqlalchemy import select, func
            result = await session.execute(select(func.count()).select_from(HTSCode))
            count = result.scalar()
            if count > 0:
                print(f"Database already has {count} HTS codes. Skipping seed.")
                return

            # Seed HTS codes
            for data in HTS_CODES:
                hts = HTSCode(
                    code=data["code"],
                    level=_determine_level(data["code"]),
                    description=data["description"],
                    parent_code=data["parent_code"],
                )
                session.add(hts)
            print(f"Seeded {len(HTS_CODES)} HTS codes.")

            # Seed tariff rules
            for data in TARIFF_RULES:
                rule = TariffRule(**data)
                session.add(rule)
            print(f"Seeded {len(TARIFF_RULES)} tariff rules.")

            # Seed exclusions
            for data in EXCLUSIONS:
                exclusion = Exclusion(**data)
                session.add(exclusion)
            print(f"Seeded {len(EXCLUSIONS)} exclusions.")

            # Seed FX rates
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
