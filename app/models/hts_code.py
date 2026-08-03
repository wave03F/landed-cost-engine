import uuid
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class HTSCode(Base):
    """
    Harmonized Tariff Schedule code with hierarchical structure.

    Levels:
    - chapter: 2-digit (e.g. "84" for Nuclear reactors, boilers, machinery)
    - heading: 4-digit (e.g. "8483" for Transmission shafts and cranks)
    - subheading: 6+ digit (e.g. "8483.40" for Gears and gearing)

    Hierarchy is maintained via parent_code (application-level, no FK constraint)
    to allow flexible insertion order during seeding.
    """

    __tablename__ = "hts_codes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    level: Mapped[str] = mapped_column(String(20), nullable=False)  # chapter, heading, subheading
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    parent_code: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
