import uuid
from datetime import date
from sqlalchemy import String, Float, Date, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class FXRate(Base):
    """
    Foreign exchange rate for a specific currency pair on a specific date.

    Used to convert invoice values from source currency (e.g. CNY) to USD
    for customs valuation purposes.
    """

    __tablename__ = "fx_rates"
    __table_args__ = (
        UniqueConstraint("from_currency", "to_currency", "date", name="uq_fx_rate_pair_date"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    from_currency: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    to_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    rate: Mapped[float] = mapped_column(Float, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
