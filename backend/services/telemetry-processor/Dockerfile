FROM python:3.11-slim

WORKDIR /app

COPY backend/services/telemetry-processor/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPYbackend/services/telemetry-processor/app ./app/

CMD ["python", "-m", "app.main"]
