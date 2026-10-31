# Production Dockerfile for CIT Campus Scheduling Platform Backend
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies required for OR-Tools & Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy dataset and validation data needed at runtime
COPY data/ /app/data/
COPY exports/ /app/exports/
COPY scripts/ /app/scripts/
COPY validator.py /app/validator.py

# Copy backend source
COPY backend/app/ /app/app/

ENV PYTHONPATH=/app
ENV ENVIRONMENT=production
ENV PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health/ready || exit 1

CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

