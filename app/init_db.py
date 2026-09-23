"""
Database initialization and seeding script.

Usage:
    python -m app.init_db                 # create tables + seed (best-effort)
    python -m app.init_db <DATABASE_URL>  # override DB URL
    python -m app.init_db --strict        # fail hard if DB is unreachable

This creates all tables and loads seed data from real US tariff sources.

By default the runner is **best-effort**: if the database is not reachable
(e.g. during a Render build step before the DB network is ready) it logs a
warning and exits 0, so the deploy is not blocked. The application's startup
lifespan will create tables and seed again once the DB is reachable at runtime.
Pass --strict to make connection failures fatal (exit 1).
"""

import asyncio
import sys

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.database import Base
from app.config import get_settings
from app.models import HTSCode, TariffRule, Exclusion, FXRate
from app.seed_data import HTS_CODES, TARIFF_RULES, EXCLUSIONS, FX_RATES


def _determine_level(code: str) -> str:
    """Determine HTS level from code format."""
    clean = code.replace(".", "")
    if len(clean) <= 2:
        return "chapter"
    elif len(clean) <= 4:
        return "heading"
    else:
        return "subheading"


async def seed_data_into_session(session: AsyncSession) -> None:
    """Seed reference data into an existing session (idempotent).

    Safe to run multiple times: only inserts rows that are missing.
    The caller is responsible for committing the transaction.
    """
    # HTS codes — add any missing ones
    result = await session.execute(select(func.count()).select_from(HTSCode))
    hts_count = result.scalar() or 0
    if hts_count == 0:
        for data in HTS_CODES:
            session.add(
                HTSCode(
                    code=data["code"],
                    level=_determine_level(data["code"]),
                    description=data["description"],
                    parent_code=data["parent_code"],
                )
            )
        print(f"Seeded {len(HTS_CODES)} HTS codes.")
    elif hts_count < len(HTS_CODES):
        existing_codes_result = await session.execute(select(HTSCode.code))
        existing_codes = {r[0] for r in existing_codes_result.all()}
        added = 0
        for data in HTS_CODES:
            if data["code"] not in existing_codes:
                session.add(
                    HTSCode(
                        code=data["code"],
                        level=_determine_level(data["code"]),
                        description=data["description"],
                        parent_code=data["parent_code"],
                    )
                )
                added += 1
        print(f"Added {added} new HTS codes (total now: {hts_count + added}).")
    else:
        print(f"HTS codes up to date ({hts_count}).")

    # Tariff rules — add any missing ones
    result = await session.execute(select(func.count()).select_from(TariffRule))
    rule_count = result.scalar() or 0
    if rule_count < len(TARIFF_RULES):
        existing = await session.execute(
            select(TariffRule.hts_code_pattern, TariffRule.origin_country, TariffRule.tariff_type)
        )
        existing_keys = {(r[0], r[1], r[2]) for r in existing.all()}
        added = 0
        for data in TARIFF_RULES:
            key = (data["hts_code_pattern"], data["origin_country"], data["tariff_type"])
            if key not in existing_keys:
                session.add(TariffRule(**data))
                added += 1
        print(f"Added {added} new tariff rules (total now: {rule_count + added}).")
    else:
        print(f"Tariff rules up to date ({rule_count}).")

    # Exclusions — seed if empty
    result = await session.execute(select(func.count()).select_from(Exclusion))
    if (result.scalar() or 0) == 0:
        for data in EXCLUSIONS:
            session.add(Exclusion(**data))
        print(f"Seeded {len(EXCLUSIONS)} exclusions.")

    # FX rates — seed if empty
    result = await session.execute(select(func.count()).select_from(FXRate))
    if (result.scalar() or 0) == 0:
        for data in FX_RATES:
            session.add(FXRate(**data))
        print(f"Seeded {len(FX_RATES)} FX rates.")


async def init_database(database_url: str | None = None) -> None:
    """Create all tables and seed initial data (assumes DB is reachable)."""
    url = database_url or get_settings().async_database_url
    engine = create_async_engine(url, echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully.")

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        async with session.begin():
            await seed_data_into_session(session)

    await engine.dispose()
    print("Database initialization complete!")


async def _init_with_retry(
    database_url: str | None, strict: bool, attempts: int = 3, delay_seconds: float = 3.0
) -> int:
    """Run init_database with retries. Returns a process exit code.

    On repeated connection failures: exit 1 if strict, else exit 0 (best-effort)
    so a deploy build step is not blocked — the app startup will retry seeding.
    """
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            await init_database(database_url)
            return 0
        except OSError as e:
            # socket.gaierror and connection errors subclass OSError
            last_error = e
            print(f"[init_db] DB not reachable (attempt {attempt}/{attempts}): {e}")
            if attempt < attempts:
                await asyncio.sleep(delay_seconds)
        except Exception as e:  # noqa: BLE001 — surface anything unexpected
            last_error = e
            print(f"[init_db] Unexpected error (attempt {attempt}/{attempts}): {type(e).__name__}: {e}")
            if attempt < attempts:
                await asyncio.sleep(delay_seconds)

    if strict:
        print(f"[init_db] FAILED after {attempts} attempts (strict mode): {last_error}")
        return 1

    print(
        "[init_db] Could not initialize the database now; continuing anyway "
        "(best-effort). The app will create tables and seed on startup once "
        "the database is reachable."
    )
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    strict = "--strict" in args
    positional = [a for a in args if not a.startswith("--")]
    url = positional[0] if positional else None
    exit_code = asyncio.run(_init_with_retry(url, strict=strict))
    sys.exit(exit_code)
