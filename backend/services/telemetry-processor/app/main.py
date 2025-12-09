import json
import os
import time
from datetime import datetime

from confluent_kafka import Consumer
from pydantic import BaseModel, ValidationError

from sqlalchemy import create_engine, Column, String, Float, DateTime, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from sqlalchemy.exc import SQLAlchemyError, OperationalError

from backend.libs.common.telemetry_models import TelemetryPoint  # shared model
from backend.libs.db.init_db import init_db 

from prometheus_client import Counter, Histogram, start_http_server


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


# # Optional: ensure table exists (dev helper – in prod you'd use migrations)
# Base.metadata.create_all(bind=engine)


# ---- Prometheus Metrics -----------------------------------------------------

METRICS_PORT = int(os.getenv("METRICS_PORT", "8002"))

TELEMETRY_CONSUMED = Counter(
    "telemetry_consumed_total",
    "Total number of telemetry messages consumed from Kafka",
)

TELEMETRY_PARSE_ERRORS = Counter(
    "telemetry_parse_errors_total",
    "Total number of telemetry messages that failed JSON/Pydantic validation",
)

TELEMETRY_DB_ERRORS = Counter(
    "telemetry_db_errors_total",
    "Total number of database errors during telemetry processing",
)

TELEMETRY_PROCESSING_TIME = Histogram(
    "telemetry_processing_seconds",
    "Time spent processing telemetry messages (including DB write)",
)

def wait_for_db(max_attempts: int = 10, delay: float = 2.0):
    for attempt in range(1, max_attempts + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("[telemetry-processor] Database is up.")
            return
        except OperationalError as e:
            print(f"[telemetry-processor] DB not ready (attempt {attempt}/{max_attempts}): {e}")
            time.sleep(delay)
        except Exception as e:
            # Log unexpected errors but keep retrying (optional)
            print(f"[telemetry-processor] Unexpected DB error (attempt {attempt}/{max_attempts}): {e}")
            time.sleep(delay)
    raise RuntimeError("Database is not ready after multiple attempts.")


def process_message(db: Session, msg: TelemetryPoint):
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
    wait_for_db()
    
    if os.getenv("INIT_DB", "false").lower() == "true":
        init_db()   

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
    print(f"[telemetry-processor] exposing metrics on :{METRICS_PORT}/metrics")

    start_http_server(METRICS_PORT)

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
                telemetry = TelemetryPoint(**payload)
            except (json.JSONDecodeError, ValidationError) as e:
                print(f"Failed to parse message: {e}")
                TELEMETRY_PARSE_ERRORS.inc()
                continue

            db = SessionLocal()
            try:
                with TELEMETRY_PROCESSING_TIME.time():
                    process_message(db, telemetry)
                    db.commit()
                
                TELEMETRY_CONSUMED.inc()  
                consumer.commit(msg)
            except SQLAlchemyError as e:
                db.rollback()
                TELEMETRY_DB_ERRORS.inc()
                print(f"DB error: {e}")
            finally:
                db.close()

    except KeyboardInterrupt:
        print("Shutting down consumer...")
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
