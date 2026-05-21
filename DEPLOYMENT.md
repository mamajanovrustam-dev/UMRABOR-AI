# UMRABOR — Deployment

Развёртывание на VPS под `umrabor.uz` с поддоменами.

## Архитектура (production)

```
                       ┌─────────────────────┐
                       │   Cloudflare DNS    │
                       │     umrabor.uz      │
                       └──────────┬──────────┘
                                  │
                       ┌──────────▼──────────┐
                       │   Nginx (host)      │
                       │   80/443 + TLS      │
                       └──────────┬──────────┘
                                  │  proxy_pass localhost:300X
        ┌────────┬────────┬───────┴────────┬────────┬────────┐
        │        │        │                │        │        │
   :3000   :3001    :3002          :3003   :8000   :9000
   web    platform  partner         miniapp  api    minio
   (Next) (Next)    (Next)          (Nginx) (FastAPI)
                                  ┌─────┴────┐
                                  ▼          ▼
                           Postgres 16    Redis 7
```

## Требования к VPS

- **OS**: Ubuntu 22.04+ или Debian 12+
- **RAM**: минимум 4 ГБ (рекомендуется 8 ГБ)
- **CPU**: 2+ vCPU
- **Disk**: 40+ ГБ SSD
- **Software**:
  - Docker 24+ и Docker Compose v2
  - Nginx 1.24+ на хосте
  - Certbot (для Let's Encrypt)
  - Git

## Шаг 1. Подготовка сервера

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y nginx certbot python3-certbot-nginx git curl

# Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
# (перезайти в сессию)
```

## Шаг 2. DNS

Создать A-записи на все поддомены, указывающие на IP вашего VPS:

| Поддомен | Назначение |
| --- | --- |
| `umrabor.uz` (+ `www`) | Публичный сайт |
| `admin.umrabor.uz` | АРМ Платформы |
| `partner.umrabor.uz` | АРМ Партнёра |
| `miniapp.umrabor.uz` | Mini App |
| `api.umrabor.uz` | Backend |
| `files.umrabor.uz` | MinIO (опционально для публичных PDF) |

## Шаг 3. Клонирование репозитория

```bash
sudo mkdir -p /opt/umrabor
sudo chown $USER:$USER /opt/umrabor
git clone https://github.com/mamajanovrustam-dev/UMRABOR-AI.git /opt/umrabor
cd /opt/umrabor
```

## Шаг 4. Конфигурация

```bash
cp .env.production.example .env.production
nano .env.production
```

Обязательно заменить:
- `SECRET_KEY` — минимум 32 случайных символа: `openssl rand -hex 32`
- `POSTGRES_PASSWORD` — сильный пароль
- `MINIO_ROOT_PASSWORD` и `S3_SECRET_KEY`
- `DATABASE_URL` — подставить тот же пароль
- `CORS_ORIGINS` — ваши финальные домены

## Шаг 5. Запуск контейнеров и миграции

```bash
bash infra/scripts/deploy.sh --seed   # с сидами, при первом деплое
# или
bash infra/scripts/deploy.sh          # последующие деплои, без сидов
```

После этого все 6 контейнеров поднимутся:

```
docker compose -f docker-compose.production.yml ps
```

## Шаг 6. Nginx конфигурация

```bash
sudo cp infra/nginx/umrabor.uz.conf /etc/nginx/sites-available/umrabor
sudo mkdir -p /etc/nginx/snippets
sudo cp infra/nginx/snippets/umrabor-proxy.conf /etc/nginx/snippets/
sudo ln -sf /etc/nginx/sites-available/umrabor /etc/nginx/sites-enabled/umrabor
sudo rm -f /etc/nginx/sites-enabled/default

# Уберите ssl-строки временно (certbot их добавит сам)
sudo nginx -t && sudo systemctl reload nginx
```

## Шаг 7. SSL через Let's Encrypt

```bash
sudo certbot --nginx \
  -d umrabor.uz -d www.umrabor.uz \
  -d admin.umrabor.uz \
  -d partner.umrabor.uz \
  -d miniapp.umrabor.uz \
  -d api.umrabor.uz \
  --email you@example.com --agree-tos --no-eff-email
```

Certbot автоматически добавит SSL-сертификаты в nginx-конфиг и настроит auto-renew.

## Шаг 8. Проверка

После завершения должны открываться:

- https://umrabor.uz — публичный сайт
- https://admin.umrabor.uz/login — Платформа (yulia.m / Demo-2026!)
- https://partner.umrabor.uz/login — Партнёр (ibrahim.r / Demo-2026!)
- https://miniapp.umrabor.uz — Mini App
- https://api.umrabor.uz/docs — Swagger

## Обновление

```bash
cd /opt/umrabor
bash infra/scripts/deploy.sh
```

Скрипт сам подтянет последний код, пересоберёт нужные контейнеры, применит миграции.

## Бэкапы

### PostgreSQL

```bash
# В cron еженощно:
docker exec umrabor_pg pg_dump -U umrabor umrabor | gzip > /backups/umrabor-$(date +%F).sql.gz
```

### MinIO (ваучеры и загрузки)

```bash
# Через mc:
mc mirror local/umrabor-vouchers /backups/vouchers/
mc mirror local/umrabor-uploads /backups/uploads/
```

## Мониторинг

Базово достаточно:

```bash
# Логи API
docker logs -f umrabor_api

# Логи Next-фронтов
docker logs -f umrabor_platform
docker logs -f umrabor_partner
docker logs -f umrabor_web

# Состояние всех контейнеров
docker compose -f docker-compose.production.yml ps
```

## Безопасность

- ⚠️ **НЕ** держите `.env.production` в git (он в `.gitignore`)
- Поменяйте все пароли по умолчанию
- Закройте на firewall все порты кроме 22, 80, 443
- Включите `fail2ban` для SSH
- Регулярно: `apt update && apt upgrade`
- Для production отключите `--seed` режим (он чистит данные)

## Click интеграция

В v1 `CLICK_MODE=mock`. Для подключения реального Click:

1. Получить `MERCHANT_ID`, `SERVICE_ID`, `SECRET_KEY` от Click.
2. Установить `CLICK_MODE=production` в `.env.production`.
3. Реализовать webhook `/api/v1/payments/click/webhook` (заготовка — в roadmap).
4. Обновить настройки в личном кабинете Click: указать ваш webhook URL.

## Troubleshooting

- **502 Bad Gateway**: контейнер не запустился — `docker logs umrabor_<name>`.
- **404 на API**: проверьте CORS и `NEXT_PUBLIC_API_URL` в фронтах.
- **Миграция не применилась**: `docker exec -it umrabor_api alembic current`.
- **OTP не приходит** (а в dev должен возвращать `0000`): убедитесь что `ENV=production` в env.
