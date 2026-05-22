# ─── builder ───
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential libpq-dev \
      libpango-1.0-0 libpangoft2-1.0-0 \
      libcairo2 libgdk-pixbuf-2.0-0 \
      libffi-dev shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install -e .

COPY . .

# ─── runtime ───
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/usr/local/bin:$PATH

RUN apt-get update && apt-get install -y --no-install-recommends \
      libpq5 \
      libpango-1.0-0 libpangoft2-1.0-0 \
      libcairo2 libgdk-pixbuf-2.0-0 \
      shared-mime-info fonts-dejavu-core \
      curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r app && useradd -r -g app app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app
COPY --chown=app:app . .
RUN chmod +x entrypoint.sh

USER app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

CMD ["./entrypoint.sh"]
