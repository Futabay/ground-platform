FROM python:3.11-slim

WORKDIR /app

COPY backend/libs ./backend/libs

COPY backend/services/telemetry-processor/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/services/telemetry-processor/app ./app/
ENV PYTHONPATH=/app:/app/../..

CMD ["python", "-m", "app.main"]
