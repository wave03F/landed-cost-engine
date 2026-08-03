"""
Test configuration and fixtures.

Uses an in-memory SQLite database for fast, isolated tests.
Each test gets a fresh database with seed data loaded.
"""

import os

# Set env before any app imports to avoid triggering asyncpg
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from datetime import date

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import app
from app.models import HTSCode, TariffRule, Exclusion, FXRate

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_engine():
    """Create a fresh test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    """Provide a database session for tests."""
    session_factory = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def seeded_session(db_engine):
    """Provide a database session pre-loaded with seed data."""
    session_factory = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        async with session.begin():
            await _seed_test_data(session)
        yield session


@pytest_asyncio.fixture
async def client(db_engine, seeded_session):
    """Provide an async HTTP test client with seeded database."""
    session_factory = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


async def _seed_test_data(session: AsyncSession):
    """Load all seed data into the test database."""
    # Seed HTS codes
    codes = [
        HTSCode(code="84", level="chapter", description="Nuclear reactors, boilers, machinery"),
        HTSCode(code="85", level="chapter", description="Electrical machinery and equipment"),
        HTSCode(code="8483", level="heading", description="Transmission shafts and cranks; gears", parent_code="84"),
        HTSCode(code="8483.40", level="subheading", description="Gears and gearing; gear boxes", parent_code="8483"),
        HTSCode(code="8483.10", level="subheading", description="Transmission shafts", parent_code="8483"),
        HTSCode(code="8482", level="heading", description="Ball or roller bearings", parent_code="84"),
        HTSCode(code="8482.10", level="subheading", description="Ball bearings", parent_code="8482"),
        HTSCode(code="8501", level="heading", description="Electric motors and generators", parent_code="84"),
        HTSCode(code="8501.52", level="subheading", description="AC motors 750W-75kW", parent_code="8501"),
        HTSCode(code="8504", level="heading", description="Electrical transformers", parent_code="85"),
        HTSCode(code="8504.40", level="subheading", description="Static converters", parent_code="8504"),
        HTSCode(code="8517", level="heading", description="Telephone sets", parent_code="85"),
        HTSCode(code="8517.12", level="subheading", description="Smartphones", parent_code="8517"),
        HTSCode(code="8542", level="heading", description="Electronic integrated circuits", parent_code="85"),
        HTSCode(code="8542.31", level="subheading", description="Processors and controllers", parent_code="8542"),
    ]
    session.add_all(codes)

    # Seed MFN rules
    mfn_rules = [
        TariffRule(id="mfn-8483", tariff_type="MFN", hts_code_pattern="8483",
                   origin_country="CN", rate=0.025, effective_from=date(2000, 1, 1),
                   effective_to=None, stacks_with=[], mutually_exclusive_with=[],
                   description="MFN 2.5% for gears/shafts"),
        TariffRule(id="mfn-8482", tariff_type="MFN", hts_code_pattern="8482",
                   origin_country="CN", rate=0.09, effective_from=date(2000, 1, 1),
                   effective_to=None, stacks_with=[], mutually_exclusive_with=[],
                   description="MFN 9% for bearings"),
        TariffRule(id="mfn-8501", tariff_type="MFN", hts_code_pattern="8501",
                   origin_country="CN", rate=0.03, effective_from=date(2000, 1, 1),
                   effective_to=None, stacks_with=[], mutually_exclusive_with=[],
                   description="MFN 3% for electric motors"),
        TariffRule(id="mfn-8504", tariff_type="MFN", hts_code_pattern="8504",
                   origin_country="CN", rate=0.015, effective_from=date(2000, 1, 1),
                   effective_to=None, stacks_with=[], mutually_exclusive_with=[],
                   description="MFN 1.5% for transformers"),
        TariffRule(id="mfn-8517", tariff_type="MFN", hts_code_pattern="8517",
                   origin_country="CN", rate=0.0, effective_from=date(2000, 1, 1),
                   effective_to=None, stacks_with=[], mutually_exclusive_with=[],
                   description="MFN 0% for telecom (free)"),
        TariffRule(id="mfn-8542", tariff_type="MFN", hts_code_pattern="8542",
                   origin_country="CN", rate=0.0, effective_from=date(2000, 1, 1),
                   effective_to=None, stacks_with=[], mutually_exclusive_with=[],
                   description="MFN 0% for ICs (free)"),
    ]
    session.add_all(mfn_rules)

    # Seed Section 301 rules
    sec301_rules = [
        TariffRule(id="301-8483", tariff_type="SECTION_301", hts_code_pattern="8483",
                   origin_country="CN", rate=0.25, effective_from=date(2018, 7, 6),
                   effective_to=None, stacks_with=["MFN"], mutually_exclusive_with=["IEEPA"],
                   description="Section 301 List 1 - 25%"),
        TariffRule(id="301-8482", tariff_type="SECTION_301", hts_code_pattern="8482",
                   origin_country="CN", rate=0.25, effective_from=date(2018, 7, 6),
                   effective_to=None, stacks_with=["MFN"], mutually_exclusive_with=["IEEPA"],
                   description="Section 301 List 1 - 25% bearings"),
        TariffRule(id="301-8501", tariff_type="SECTION_301", hts_code_pattern="8501",
                   origin_country="CN", rate=0.25, effective_from=date(2018, 7, 6),
                   effective_to=None, stacks_with=["MFN"], mutually_exclusive_with=["IEEPA"],
                   description="Section 301 List 1 - 25% motors"),
        TariffRule(id="301-8504", tariff_type="SECTION_301", hts_code_pattern="8504",
                   origin_country="CN", rate=0.25, effective_from=date(2018, 9, 24),
                   effective_to=None, stacks_with=["MFN"], mutually_exclusive_with=["IEEPA"],
                   description="Section 301 List 3 - 25% transformers"),
    ]
    session.add_all(sec301_rules)

    # Seed Section 232 rule
    session.add(TariffRule(
        id="232-8482-10", tariff_type="SECTION_232", hts_code_pattern="8482.10",
        origin_country="CN", rate=0.25, effective_from=date(2018, 3, 23),
        effective_to=None, stacks_with=["MFN"], mutually_exclusive_with=["IEEPA"],
        description="Section 232 - 25% steel derivative (ball bearings)",
    ))

    # Seed IEEPA rules (2025+)
    ieepa_rules = [
        TariffRule(id="ieepa-84", tariff_type="IEEPA", hts_code_pattern="84",
                   origin_country="CN", rate=0.145, effective_from=date(2025, 4, 9),
                   effective_to=None, stacks_with=["MFN"],
                   mutually_exclusive_with=["SECTION_301", "SECTION_232"],
                   description="IEEPA 145% reciprocal - Ch 84"),
        TariffRule(id="ieepa-85", tariff_type="IEEPA", hts_code_pattern="85",
                   origin_country="CN", rate=0.145, effective_from=date(2025, 4, 9),
                   effective_to=None, stacks_with=["MFN"],
                   mutually_exclusive_with=["SECTION_301", "SECTION_232"],
                   description="IEEPA 145% reciprocal - Ch 85"),
    ]
    session.add_all(ieepa_rules)

    # Seed exclusions
    exclusions = [
        Exclusion(id="excl-8542-31", hts_code="8542.31", tariff_type="IEEPA",
                  origin_country="CN", effective_from=date(2025, 4, 9), effective_to=None,
                  description="Semiconductor ICs excluded from IEEPA"),
        Exclusion(id="excl-8517-12-301", hts_code="8517.12", tariff_type="SECTION_301",
                  origin_country="CN", effective_from=date(2025, 4, 11),
                  effective_to=date(2025, 7, 9),
                  description="Temporary smartphone exclusion"),
    ]
    session.add_all(exclusions)

    # Seed FX rates
    fx_rates = [
        FXRate(from_currency="CNY", to_currency="USD", rate=0.1389, date=date(2026, 8, 1)),
        FXRate(from_currency="CNY", to_currency="USD", rate=0.1388, date=date(2026, 7, 31)),
        FXRate(from_currency="CNY", to_currency="USD", rate=0.1380, date=date(2026, 7, 1)),
        FXRate(from_currency="CNY", to_currency="USD", rate=0.1400, date=date(2025, 4, 9)),
        FXRate(from_currency="CNY", to_currency="USD", rate=0.1395, date=date(2025, 1, 1)),
        FXRate(from_currency="CNY", to_currency="USD", rate=0.1420, date=date(2024, 1, 1)),
        FXRate(from_currency="CNY", to_currency="USD", rate=0.1410, date=date(2018, 7, 6)),
    ]
    session.add_all(fx_rates)
