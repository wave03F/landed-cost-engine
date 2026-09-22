from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hts_code import HTSCode
from app.models.tariff_rule import TariffRule
from app.models.exclusion import Exclusion
from app.schemas.hts import HTSCodeCreate, HTSCodeUpdate


class HTSService:
    """Service for HTS code management and lookup."""

    def __init__(self, db: AsyncSession):
        self.db = db

    def _determine_level(self, code: str) -> str:
        """Determine HTS level from code format."""
        clean = code.replace(".", "")
        if len(clean) <= 2:
            return "chapter"
        elif len(clean) <= 4:
            return "heading"
        else:
            return "subheading"

    async def search(self, query: str, level: str | None) -> list[HTSCode]:
        """Search HTS codes by prefix or description."""
        stmt = select(HTSCode)
        if query:
            stmt = stmt.where(
                (HTSCode.code.startswith(query)) | (HTSCode.description.ilike(f"%{query}%"))
            )
        if level:
            stmt = stmt.where(HTSCode.level == level)
        stmt = stmt.order_by(HTSCode.code).limit(50)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_code(self, code: str) -> HTSCode:
        """Get a specific HTS code, raising 404 if not found."""
        stmt = select(HTSCode).where(HTSCode.code == code)
        result = await self.db.execute(stmt)
        hts = result.scalar_one_or_none()
        if not hts:
            raise HTTPException(status_code=404, detail=f"HTS code '{code}' not found")
        return hts

    async def validate_code_exists(self, code: str) -> bool:
        """Check if an HTS code exists in the database."""
        # Try exact match first, then prefix match (for subheadings)
        stmt = select(HTSCode).where(HTSCode.code == code)
        result = await self.db.execute(stmt)
        if result.scalar_one_or_none():
            return True

        # Try matching as a prefix (e.g. "8483.40" matches parent "8483")
        clean = code.replace(".", "")
        for length in [len(clean), 4, 2]:
            prefix = clean[:length]
            formatted = self._format_code(prefix)
            stmt = select(HTSCode).where(HTSCode.code == formatted)
            result = await self.db.execute(stmt)
            if result.scalar_one_or_none():
                return True
        return False

    def _format_code(self, clean_code: str) -> str:
        """Format a clean code back to standard format."""
        if len(clean_code) <= 4:
            return clean_code
        return f"{clean_code[:4]}.{clean_code[4:]}"

    async def create(self, data: HTSCodeCreate) -> HTSCode:
        """Create a new HTS code entry."""
        level = self._determine_level(data.code)

        # Check for duplicates
        stmt = select(HTSCode).where(HTSCode.code == data.code)
        result = await self.db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(status_code=409, detail=f"HTS code '{data.code}' already exists")

        hts = HTSCode(
            code=data.code,
            level=level,
            description=data.description,
            parent_code=data.parent_code,
        )
        self.db.add(hts)
        await self.db.flush()
        return hts

    async def update(self, code: str, data: HTSCodeUpdate) -> HTSCode:
        """Update an existing HTS code's description/parent. Raises 404 if not found."""
        hts = await self.get_by_code(code)
        if data.description is not None:
            hts.description = data.description
        if data.parent_code is not None:
            hts.parent_code = data.parent_code
        await self.db.flush()
        return hts

    async def delete(self, code: str) -> None:
        """Delete an HTS code. Raises 404 if not found.

        Referential guard: refuses (HTTP 409) if any tariff rule or exclusion
        still references this code, so the calculation engine never ends up with
        dangling references. Detach those references first (or delete them) before
        removing the HTS code.
        """
        hts = await self.get_by_code(code)

        # Match both dotted and undotted forms of the code (e.g. "8483.40" / "848340")
        code_variants = {code, code.replace(".", "")}
        clean = code.replace(".", "")
        if len(clean) > 4:
            code_variants.add(f"{clean[:4]}.{clean[4:]}")

        rule_count = await self._count_referencing_rules(code_variants)
        exclusion_count = await self._count_referencing_exclusions(code_variants)
        if rule_count or exclusion_count:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Cannot delete HTS code '{code}': it is still referenced by "
                    f"{rule_count} tariff rule(s) and {exclusion_count} exclusion(s). "
                    "Remove or reassign those first."
                ),
            )

        await self.db.delete(hts)
        await self.db.flush()

    async def _count_referencing_rules(self, code_variants: set[str]) -> int:
        stmt = select(func.count()).select_from(TariffRule).where(
            TariffRule.hts_code_pattern.in_(code_variants)
        )
        result = await self.db.execute(stmt)
        return int(result.scalar() or 0)

    async def _count_referencing_exclusions(self, code_variants: set[str]) -> int:
        stmt = select(func.count()).select_from(Exclusion).where(
            Exclusion.hts_code.in_(code_variants)
        )
        result = await self.db.execute(stmt)
        return int(result.scalar() or 0)
