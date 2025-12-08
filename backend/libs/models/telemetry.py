from sqlalchemy import Column, String, Float, DateTime
from backend.libs.db.base import Base


class TelemetryORM(Base):
    __tablename__ = "telemetry"

    # Primary key: composite or single, for now simple surrogate key is fine
    # but for timeseries we often use (timestamp, satellite_id, parameter).
    # To keep it simple: no id, but you *can* add one if you like.

    timestamp = Column(DateTime, primary_key=True, index=True)
    satellite_id = Column(String, primary_key=True, index=True)
    subsystem = Column(String, nullable=False)
    parameter = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False, default="")
    status = Column(String, nullable=False, default="OK")
