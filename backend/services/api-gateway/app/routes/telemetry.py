from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db
from backend.libs.models.telemetry import TelemetryORM
from backend.libs.common.telemetry_models import TelemetryPoint

router = APIRouter()

@router.get("/", response_model=list[TelemetryPoint])
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