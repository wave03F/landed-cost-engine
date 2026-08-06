import uuid
from datetime import datetime, date
from sqlalchemy import String, Date, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class CalculationLog(Base):
    """
    Audit trail for every landed cost calculation performed.

    Stores the full input, matched rules, exclusions, and result so that
    past calculations can be reproduced and audited even if rules change later.
    """

    __tablename__ = "calculation_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)  # null = anonymous/API key
    hts_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    import_date: Mapped[date] = mapped_column(Date, nullable=False)
    origin_country: Mapped[str] = mapped_column(String(5), nullable=False)
    input_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    matched_rules: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    exclusions_applied: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    result_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
