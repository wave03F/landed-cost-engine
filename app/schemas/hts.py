from pydantic import BaseModel, Field


class HTSCodeCreate(BaseModel):
    code: str = Field(..., description="HTS code (e.g. '84', '8483', '8483.40')")
    description: str = Field(..., description="Description of the HTS classification")
    parent_code: str | None = Field(default=None, description="Parent HTS code for hierarchy")

    model_config = {"json_schema_extra": {"examples": [{"code": "8483.40", "description": "Gears and gearing; ball or roller screws; gear boxes and other speed changers", "parent_code": "8483"}]}}


class HTSCodeUpdate(BaseModel):
    description: str | None = Field(default=None, description="Updated description")
    parent_code: str | None = Field(default=None, description="Updated parent HTS code")


class HTSCodeResponse(BaseModel):
    id: str
    code: str
    level: str  # chapter, heading, subheading
    description: str
    parent_code: str | None = None

    model_config = {"from_attributes": True}
