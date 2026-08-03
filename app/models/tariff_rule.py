import uuid
from datetime import date
from sqlalchemy import String, Float, Date, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TariffRule(Base):
    """
    A tariff rule that defines a duty rate for specific goods from specific origins.

    Temporal versioning: each rule has effective_from/effective_to to support
    time-based rule resolution. Only rules where effective_from <= import_date
    and (effective_to is NULL or effective_to >= import_date) are considered.

    Stacking logic:
    - stacks_with: list of tariff types that this rule can be added on top of
    - mutually_exclusive_with: list of tariff types where only the higher rate applies
    """

    __tablename__ = "tariff_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tariff_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    hts_code_pattern: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    origin_country: Mapped[str] = mapped_column(String(5), nullable=False, index=True)
    rate: Mapped[float] = mapped_column(Float, nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    stacks_with: Mapped[list] = mapped_column(JSON, default=list)
    mutually_exclusive_with: Mapped[list] = mapped_column(JSON, default=list)
    description: Mapped[str] = mapped_column(String(500), default="")
    source_reference: Mapped[str] = mapped_column(String(500), default="")
