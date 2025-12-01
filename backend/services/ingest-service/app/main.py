import json
import os
import time
from datetime import datetime
from random import random

from confluent_kafka import Producer
# from pydantic import BaseModel
from backend.libs.common.telemetry_models import TelemetryPoint  # via PYTHONPATH



KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TELEMETRY_TOPIC = os.getenv("TELEMETRY_TOPIC", "telemetry.raw")


# class TelemetryMessage(BaseModel):
#     timestamp: datetime
#     satellite_id: str
#     subsystem: str
#     parameter: str
#     value: float
#     unit: str = "V"
#     status: str = "OK"


def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")
    else:
        print(f"Delivered to {msg.topic()} [{msg.partition()}] offset {msg.offset()}")


def main():
    producer_conf = {"bootstrap.servers": KAFKA_BROKER}
    producer = Producer(producer_conf)

    print(f"[ingest-service] producing to {TELEMETRY_TOPIC} on {KAFKA_BROKER}")

    while True:
        msg = TelemetryMessage(
            timestamp=datetime.utcnow(),
            satellite_id="SAT-001",
            subsystem="EPS",
            parameter="battery_voltage",
            value=3.5 + random() * 0.2,  # 3.5–3.7 V
            unit="V",
            status="OK",
        )

        producer.produce(
            TELEMETRY_TOPIC,
            value=msg.model_dump_json().encode("utf-8"),
            callback=delivery_report,
        )
        producer.poll(0)
        time.sleep(1)


if __name__ == "__main__":
    main()
