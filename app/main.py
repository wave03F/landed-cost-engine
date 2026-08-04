from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.database import get_engine, Base
from app.config import get_settings
from app.routers import calculation, hts_codes, tariff_rules, fx_rates, audit


async def _ensure_database_exists():
    """Create the target database if it doesn't exist (PostgreSQL only)."""
    settings = get_settings()
    url = settings.async_database_url
    if "postgresql" not in url:
        return

    db_name = url.rsplit("/", 1)[-1]
    admin_url = url.rsplit("/", 1)[0] + "/postgres"

    admin_engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT", echo=False)
    try:
        async with admin_engine.connect() as conn:
            result = await conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
                {"dbname": db_name},
            )
            if not result.scalar():
                await conn.execute(text(f'CREATE DATABASE "{db_name}"'))
                print(f"Created database '{db_name}'")
    except Exception as e:
        print(f"Warning: Could not auto-create database: {e}")
    finally:
        await admin_engine.dispose()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database and tables on startup."""
    await _ensure_database_exists()
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Landed-Cost Engine",
    summary="Calculate accurate US import landed costs with layered tariff rules",
    description="""
## Overview

This API calculates the **true landed cost** of goods imported from China to the United States,
applying all applicable tariff layers:

| Tariff Type | Description | Typical Rate |
|-------------|-------------|--------------|
| **MFN** | Base Most Favored Nation duty | 0-9% |
| **Section 301** | China-specific punitive tariffs (2018+) | 25% |
| **Section 232** | National security tariffs (steel/aluminum) | 25% |
| **IEEPA** | Reciprocal tariffs (2025+) | 14.5% |

## Key Features

- **Temporal rule resolution** — returns the correct rate for any historical date
- **Stacking logic** — handles rules that stack vs. rules that are mutually exclusive
- **Exclusion tracking** — temporary exemptions are automatically applied
- **Currency conversion** — accepts CNY values, converts via historical FX rates
- **Audit trail** — every calculation is logged with full traceability

## Authentication

All endpoints require an `X-API-Key` header. Get your key from the system administrator.
If no keys are configured (development mode), auth is disabled.
""",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    contact={"name": "API Support"},
    license_info={"name": "MIT"},
)

# CORS — allow frontend to call this API from browser
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(calculation.router, tags=["Landed Cost Calculation"])
app.include_router(hts_codes.router, tags=["HTS Code Lookup"])
app.include_router(tariff_rules.router, tags=["Tariff Rules"])
app.include_router(fx_rates.router, tags=["Exchange Rates"])
app.include_router(audit.router, tags=["Audit Trail"])


@app.get("/health", tags=["System"], summary="Health check")
async def health_check():
    """Returns service health status. No authentication required."""
    return {"status": "healthy", "service": "landed-cost-engine"}
