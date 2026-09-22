from datetime import datetime
from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    avatar_url: str | None = None
    oauth_provider: str
    role: str
    daily_calculations: int
    last_calculation_date: str | None = None
    created_at: datetime
    last_login_at: datetime | None = None

    model_config = {"from_attributes": True}


class UserRoleUpdate(BaseModel):
    role: str = Field(..., description="New role: 'user' or 'admin'")
