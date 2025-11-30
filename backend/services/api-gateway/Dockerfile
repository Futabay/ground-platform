FROM python:3.11-slim

WORKDIR /app

# 1) Copy shared backend libs (so `backend.libs.common` is available)
COPY backend/libs ./backend/libs

# 2) Copy requirements for this service
COPY backend/services/api-gateway/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 3) Copy the api-gateway app code
COPY backend/services/api-gateway/app ./app/

# 4) Make sure Python can import from /app (so `backend` is a top-level package)
ENV PYTHONPATH=/app

RUN apt-get update && apt-get install -y procps 

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
