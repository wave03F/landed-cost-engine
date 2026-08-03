from datetime import datetime, date
from pydantic import BaseModel


class CalculationLogResponse(BaseModel):
    id: str
    hts_code: str
    import_date: date
    origin_country: str
    input_data: dict
    matched_rules: list[str]
    exclusions_applied: list[str]
    result_data: dict
    calculated_at: datetime

    model_config = {"from_attributes": True}
