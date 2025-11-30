from pydantic import BaseModel
from datetime import datetime


class TelemetryPoint(BaseModel):
    timestamp: datetime
    satellite_id: str
    subsystem: str
    parameter: str
    value: float
    unit: str = ""
    status: str = "OK"   # OK / WARN / CRITICAL
