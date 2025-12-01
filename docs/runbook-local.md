# **📘 Week 1 — Days 1–4 (Ground Data Platform Portfolio Project)**

**Goal:** Build the backend skeleton, start all infrastructure, initialize the database, add ingest/processor pipelines, and build a frontend skeleton using React + Vite + TypeScript.

---

# **Day 1 — Project Setup + Repository Structure**

### ✅ 1. Create the Git repository

```bash
mkdir ground-platform
cd ground-platform
git init
```

### ✅ 2. Create top-level directory structure

```
ground-platform/
│
├── backend/
│   ├── libs/
│   │   └── common/
│   │       ├── telemetry_models.py
│   │       └── __init__.py
│   └── services/
│       ├── api-gateway/
│       │   ├── app/
│       │   │   ├── main.py
│       │   │   ├── routes/
│       │   │   │   ├── health.py
│       │   │   │   └── telemetry.py
│       │   │   └── models/
│       │   ├── requirements.txt
│       │   └── Dockerfile
│       ├── ingest-service/
│       │   ├── app/
│       │   ├── requirements.txt
│       │   └── Dockerfile
│       └── telemetry-processor/
│           ├── app/
│           ├── requirements.txt
│           └── Dockerfile
│
├── frontend/
│   └── dashboard/
│       ├── src/
│       ├── package.json
│       └── Dockerfile
│
├── ops/
│   ├── docker-compose/
│   │   └── docker-compose.local.yml
│   └── README.md
│
└── docs/
    └── week1-day1-4.md
```

---

# **Day 2 — Backend Skeleton (FastAPI + Shared Models + Dockerfiles)**

### ✅ 1. Add **FastAPI skeleton** in `api-gateway`

**`backend/services/api-gateway/app/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.health import router as health_router
from app.routes.telemetry import router as telemetry_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="Ground Data Platform API Gateway",
        version="0.1.0",
    )

    # CORS for frontend dev
    origins = ["http://localhost:5173", "http://localhost:3000"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router, prefix="/health", tags=["Health"])
    app.include_router(telemetry_router, prefix="/telemetry", tags=["Telemetry"])

    return app

app = create_app()
```

### ✅ 2. Basic `/health` endpoint

**`backend/services/api-gateway/app/routes/health.py`**

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def health():
    return {"status": "ok", "service": "api-gateway"}
```

### ✅ 3. Add shared Pydantic models

**`backend/libs/common/telemetry_models.py`**

```python
from pydantic import BaseModel
from datetime import datetime

class TelemetryPoint(BaseModel):
    timestamp: datetime
    satellite_id: str
    subsystem: str
    parameter: str
    value: float
    unit: str | None = None
    status: str | None = None
```

### ✅ 4. Create Dockerfile

**`backend/services/api-gateway/Dockerfile`**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy shared libs + service code
COPY backend/libs ./backend/libs
COPY backend/services/api-gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/services/api-gateway/app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

# **Day 3 — Local Infrastructure (Postgres + Kafka + API Gateway)**

### ✅ 1. Build the local infra with Docker Compose

**`ops/docker-compose/docker-compose.local.yml`** (simplified)

```yaml
services:
  postgres:
    image: postgres:15
    container_name: ground-postgres
    environment:
      POSTGRES_USER: ground
      POSTGRES_PASSWORD: ground
      POSTGRES_DB: ground
    ports:
      - "5432:5432"
    networks:
      - ground-net
    volumes:
      - postgres_data:/var/lib/postgresql/data

  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    container_name: ground-zookeeper
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
    networks:
      - ground-net

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    container_name: ground-kafka
    depends_on:
      - zookeeper
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: ground-zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    ports:
      - "9092:9092"
    networks:
      - ground-net

  api-gateway:
    build:
      context: ../..
      dockerfile: backend/services/api-gateway/Dockerfile
    container_name: ground-api-gateway
    depends_on:
      - postgres
      - kafka
    ports:
      - "8000:8000"
    networks:
      - ground-net

networks:
  ground-net:

volumes:
  postgres_data:
```

### Run everything:

```bash
cd ops/docker-compose
docker compose -f docker-compose.local.yml up --build
```

### Verify:

```bash
curl http://localhost:8000/health
```

Expect:

```json
{"status":"ok","service":"api-gateway"}
```

---

# **Day 4 — Ingest + Processor Services (Kafka Production + PG Storage)**

### ✅ 1. Create telemetry ingest service

**`backend/services/ingest-service/app/main.py`**

```python
import os
import time
import json
from kafka import KafkaProducer
from datetime import datetime
import random

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC = os.getenv("TELEMETRY_TOPIC", "telemetry.raw")

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

def generate_fake():
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "satellite_id": "SAT-001",
        "subsystem": "EPS",
        "parameter": "battery_voltage",
        "value": round(random.uniform(3.4, 4.1), 3),
        "unit": "V",
        "status": "OK",
    }

while True:
    msg = generate_fake()
    producer.send(TOPIC, msg)
    producer.flush()
    print("Produced:", msg)
    time.sleep(1)
```

### Dockerfile:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/services/ingest-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/services/ingest-service/app ./app
CMD ["python", "-m", "app.main"]
```

---

### ✅ 2. Create telemetry processor service

Consumes Kafka → writes rows into Postgres.

**`backend/services/telemetry-processor/app/main.py`**

```python
import os
import json
import psycopg2
from kafka import KafkaConsumer

DB = dict(
    host=os.getenv("DB_HOST", "postgres"),
    user=os.getenv("DB_USER", "ground"),
    password=os.getenv("DB_PASSWORD", "ground"),
    dbname=os.getenv("DB_NAME", "ground"),
    port=os.getenv("DB_PORT", 5432),
)

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC = os.getenv("TELEMETRY_TOPIC", "telemetry.raw")

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
)

conn = psycopg2.connect(**DB)
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS telemetry (
        timestamp TIMESTAMPTZ,
        satellite_id TEXT,
        subsystem TEXT,
        parameter TEXT,
        value DOUBLE PRECISION,
        unit TEXT,
        status TEXT
    )
""")
conn.commit()

for msg in consumer:
    t = msg.value
    cur.execute("""
        INSERT INTO telemetry(timestamp, satellite_id, subsystem, parameter, value, unit, status)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (
        t["timestamp"], t["satellite_id"], t["subsystem"], t["parameter"],
        t["value"], t.get("unit"), t.get("status")
    ))
    conn.commit()
    print("Inserted telemetry row")
```

Add it to `docker-compose.local.yml` as another service.

---

### 💾 Verify Postgres ingestion:

```bash
docker exec -it ground-postgres psql -U ground -d ground
```

```sql
SELECT COUNT(*) FROM telemetry;
SELECT * FROM telemetry LIMIT 5;
```

Expect growing rows.

---

# ✔ Summary (Days 1–4)

By the end of Day 4 you have:

* Full backend skeleton
* Kafka pipeline (producer → consumer)
* Postgres ingestion
* Correct Docker Compose environment
* Verified `/health` and `/telemetry` data flow
* Project directory structure ready for the frontend


