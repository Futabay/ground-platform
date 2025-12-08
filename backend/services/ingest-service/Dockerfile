FROM python:3.11-slim

WORKDIR /app

COPY backend/libs ./backend/libs

COPY backend/services/ingest-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/services/ingest-service/app ./app/
ENV PYTHONPATH=/app

CMD ["python", "-m", "app.main"]
