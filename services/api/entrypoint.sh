#!/bin/sh
# Entrypoint для production контейнера UMRABOR API.
# - применяет миграции
# - загружает сиды только если SEED_ON_BOOT=true (для staging-первого запуска)
# - запускает uvicorn

set -e

echo "▸ Running Alembic migrations..."
alembic upgrade head

if [ "${SEED_ON_BOOT:-false}" = "true" ]; then
    echo "▸ Loading seed data..."
    python -m app.scripts.seed || echo "(seed skipped, possibly already loaded)"
fi

echo "▸ Starting uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${WORKERS:-2}
