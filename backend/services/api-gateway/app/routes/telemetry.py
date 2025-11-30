from fastapi import APIRouter
from datetime import datetime, timedelta
from backend.libs.common.telemetry_models import TelemetryPoint

router = APIRouter()

@router.get("/", response_model=list[TelemetryPoint])
async def get_mock_telemetry(limit: int = 10):
    """Return mock telemetry data (for Week 1 only)."""
    now = datetime.utcnow()

    return [
        TelemetryPoint(
            timestamp=now - timedelta(seconds=i * 10),
            satellite_id="SAT-001",
            subsystem="EPS",
            parameter="battery_voltage",
            value=3.7 + (i * 0.01),
            unit="V",
            status="OK",
        )
        for i in range(limit)
    ]
