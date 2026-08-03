import uuid
from datetime import date
from sqlalchemy import String, Date
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Exclusion(Base):
    """
    A tariff exclusion that temporarily exempts specific HTS codes from a tariff type.

    For example, a Section 301 exclusion might exempt HTS 8483.40 from the 25% tariff
    during a specific date range. These are granted by USTR and have definite expiration dates.
    """

    __tablename__ = "exclusions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    hts_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    tariff_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    origin_country: Mapped[str] = mapped_column(String(5), nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    description: Mapped[str] = mapped_column(String(500), default="")
    source_reference: Mapped[str] = mapped_column(String(500), default="")
