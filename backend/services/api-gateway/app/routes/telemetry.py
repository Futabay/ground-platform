from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.telemetry import TelemetryORM
from backend.libs.common.telemetry_models import TelemetryPoint

router = APIRouter()

@router.get("/", response_model=list[TelemetryPoint])
# async def get_mock_telemetry(limit: int = 10):
#     """Return mock telemetry data (for Week 1 only)."""
#     now = datetime.utcnow()

#     return [
#         TelemetryPoint(
#             timestamp=now - timedelta(seconds=i * 10),
#             satellite_id="SAT-001",
#             subsystem="EPS",
#             parameter="battery_voltage",
#             value=3.7 + (i * 0.01),
#             unit="V",
#             status="OK",
#         )
#         for i in range(limit)
#     ]

def get_telemetry(
    satellite_id: str | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(TelemetryORM)

    if satellite_id:
        query = query.filter(TelemetryORM.satellite_id == satellite_id)

    query = query.order_by(TelemetryORM.timestamp.desc()).limit(limit)

    rows = query.all()

    return [
        TelemetryPoint(
            timestamp=row.timestamp,
            satellite_id=row.satellite_id,
            subsystem=row.subsystem,
            parameter=row.parameter,
            value=row.value,
            unit=row.unit,
            status=row.status,
        )
        for row in rows
    ]