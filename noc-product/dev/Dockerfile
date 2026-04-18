FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      libpq-dev \
      tesseract-ocr \
      poppler-utils \
      libmagic1 \
      curl \
      wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependency layer (cached across rebuilds).
COPY pyproject.toml /app/pyproject.toml
COPY README.md /app/README.md
RUN pip install --upgrade pip && \
    pip install \
      "fastapi>=0.110" \
      "uvicorn[standard]>=0.29" \
      "jinja2>=3.1" \
      "python-multipart>=0.0.9" \
      "itsdangerous>=2.2" \
      "pydantic>=2.6" \
      "pydantic-settings>=2.2" \
      "httpx>=0.27" \
      "sqlalchemy>=2.0" \
      "psycopg[binary,pool]>=3.1" \
      "alembic>=1.13" \
      "asyncpg>=0.29" \
      "pgvector>=0.2.5" \
      "langgraph>=0.0.40" \
      "pyyaml>=6.0" \
      "python-jose[cryptography]>=3.3" \
      "authlib>=1.3" \
      "minio>=7.2" \
      "hvac>=2.1" \
      "prometheus-client>=0.20" \
      "opentelemetry-api>=1.24" \
      "opentelemetry-sdk>=1.24" \
      "opentelemetry-instrumentation-fastapi>=0.45b0" \
      "tenacity>=8.2" \
      "structlog>=24.1" \
      "unstructured[pdf]>=0.13" \
      "pdfminer.six>=20231228" \
      "pytesseract>=0.3.10" \
      "python-docx>=1.1" \
      "tiktoken>=0.6" \
      "click>=8.1" \
      "filelock>=3.13"

COPY services /app/services
COPY db /app/db
COPY fixtures /app/fixtures

ENV PYTHONPATH=/app
