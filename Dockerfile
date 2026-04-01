FROM python:3.12-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

FROM base AS deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libmagic1 && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml README.md ./
COPY src ./src
COPY apps ./apps
COPY configs ./configs
COPY eval ./eval
COPY cli ./cli
COPY sdk ./sdk
RUN pip install --upgrade pip && pip install .

FROM base AS production
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 curl && rm -rf /var/lib/apt/lists/*
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin
COPY . .
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/liveness || exit 1
EXPOSE 8000
CMD ["sh", "-c", "uvicorn apps.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

FROM production AS development
RUN pip install --upgrade pip && pip install .[dev]
CMD ["sh", "-c", "uvicorn apps.api.main:app --host 0.0.0.0 --port ${PORT:-8000} --reload"]
