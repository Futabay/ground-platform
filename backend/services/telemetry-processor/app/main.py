import json
import os
from datetime import datetime

from confluent_kafka import Consumer
from pydantic import BaseModel, ValidationError

from sqlalchemy import create_engine, Column, String, Float, DateTime
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from sqlalchemy.exc import SQLAlchemyError


# ---- DB config ----
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "ground")
DB_PASSWORD = os.getenv("DB_PASSWORD", "ground")
DB_NAME = os.getenv("DB_NAME", "ground")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class TelemetryORM(Base):
    __tablename__ = "telemetry"

    timestamp = Column(DateTime, primary_key=True, index=True)
    satellite_id = Column(String, primary_key=True, index=True)
    subsystem = Column(String, nullable=False)
    parameter = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False, default="")
    status = Column(String, nullable=False, default="OK")


# Optional: ensure table exists (dev helper – in prod you'd use migrations)
Base.metadata.create_all(bind=engine)


# ---- Kafka message schema ----
class TelemetryMessage(BaseModel):
    timestamp: datetime
    satellite_id: str
    subsystem: str
    parameter: str
    value: float
    unit: str = "V"
    status: str = "OK"


def process_message(db: Session, msg: TelemetryMessage):
    obj = TelemetryORM(
        timestamp=msg.timestamp,
        satellite_id=msg.satellite_id,
        subsystem=msg.subsystem,
        parameter=msg.parameter,
        value=msg.value,
        unit=msg.unit,
        status=msg.status,
    )
    db.add(obj)


def main():
    kafka_broker = os.getenv("KAFKA_BROKER", "kafka:9092")
    telemetry_topic = os.getenv("TELEMETRY_TOPIC", "telemetry.raw")
    group_id = os.getenv("KAFKA_GROUP_ID", "telemetry-processor-group")

    conf = {
        "bootstrap.servers": kafka_broker,
        "group.id": group_id,
        "auto.offset.reset": "earliest",
    }

    consumer = Consumer(conf)
    consumer.subscribe([telemetry_topic])

    print(f"[telemetry-processor] consuming from {telemetry_topic} on {kafka_broker}")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Kafka error: {msg.error()}")
                continue

            try:
                payload = json.loads(msg.value().decode("utf-8"))
                telemetry = TelemetryMessage(**payload)
            except (json.JSONDecodeError, ValidationError) as e:
                print(f"Failed to parse message: {e}")
                continue

            db = SessionLocal()
            try:
                process_message(db, telemetry)
                db.commit()
                consumer.commit(msg)
            except SQLAlchemyError as e:
                db.rollback()
                print(f"DB error: {e}")
            finally:
                db.close()

    except KeyboardInterrupt:
        print("Shutting down consumer...")
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
