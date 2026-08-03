from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hts_code import HTSCode
from app.schemas.hts import HTSCodeCreate


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
