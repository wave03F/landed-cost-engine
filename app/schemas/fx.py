import datetime as dt
from pydantic import BaseModel, Field


class FXRateCreate(BaseModel):
    from_currency: str = Field(default="CNY", description="Source currency ISO code")
    to_currency: str = Field(default="USD", description="Target currency ISO code")
    rate: float = Field(..., gt=0, description="Exchange rate (1 unit of from_currency = rate units of to_currency)")
    rate_date: dt.date = Field(..., alias="date", description="Date for this rate")

    model_config = {"populate_by_name": True}


class FXRateResponse(BaseModel):
    id: str
    from_currency: str
    to_currency: str
    rate: float
    rate_date: dt.date = Field(validation_alias="date", serialization_alias="date")

    model_config = {"from_attributes": True, "populate_by_name": True}
