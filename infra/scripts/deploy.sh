#!/usr/bin/env bash
# UMRABOR — production deploy на VPS.
# Запускать на сервере как root или через sudo.
#
# Использование:
#   1. Скопировать репо на VPS:  git clone ... /opt/umrabor && cd /opt/umrabor
#   2. Скопировать .env.production.example → .env.production и заполнить
#   3. Запустить:  bash infra/scripts/deploy.sh
#
# Скрипт:
#   - Проверяет наличие .env.production
#   - Поднимает все контейнеры (postgres, redis, minio, api, 3 next-app, miniapp)
#   - Применяет миграции
#   - Опционально загружает сиды (только при первом деплое)
#   - Перезагружает nginx

set -euo pipefail

cd "$(dirname "$0")/../.."

if [ ! -f .env.production ]; then
    echo "ERROR: .env.production не найден. Скопируйте .env.production.example и заполните."
    exit 1
fi

echo "═══════════════════════════════════════════════════════════════════"
echo " UMRABOR · Production Deploy"
echo "═══════════════════════════════════════════════════════════════════"

echo "▸ Pull latest"
git pull --rebase --autostash

echo "▸ Build & restart containers"
docker compose -f docker-compose.production.yml --env-file .env.production pull
docker compose -f docker-compose.production.yml --env-file .env.production build
docker compose -f docker-compose.production.yml --env-file .env.production up -d

echo "▸ Wait for postgres"
until docker exec umrabor_pg pg_isready -U umrabor >/dev/null 2>&1; do
    sleep 1
done

echo "▸ Run migrations"
docker exec umrabor_api alembic upgrade head

if [ "${1:-}" = "--seed" ]; then
    echo "▸ Loading seed data (one-time)"
    docker exec umrabor_api python -m app.scripts.seed
fi

echo "▸ Reload nginx (если установлен на хосте)"
if command -v nginx >/dev/null 2>&1; then
    nginx -t && systemctl reload nginx || true
fi

echo ""
echo "✓ Deploy completed."
echo ""
echo "Сервисы (через nginx с TLS):"
echo "  https://umrabor.uz             — публичный сайт"
echo "  https://admin.umrabor.uz       — АРМ Платформы"
echo "  https://partner.umrabor.uz     — АРМ Партнёра"
echo "  https://miniapp.umrabor.uz     — Mini App"
echo "  https://api.umrabor.uz/docs    — Swagger UI"
echo ""
