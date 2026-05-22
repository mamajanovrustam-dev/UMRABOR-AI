# UMRABOR

Цифровая платформа для организации поездок **Умра** и **Хадж** на узбекистанском рынке.

## Состав

| Продукт | Стек | Поддомен |
| --- | --- | --- |
| Публичный веб-сайт | Next.js 15 | `umrabor.uz` |
| АРМ Платформы (UMRABOR Inc.) | Next.js 15 | `admin.umrabor.uz` |
| АРМ Партнёра (тур-операторы) | Next.js 15 | `partner.umrabor.uz` |
| Mini App в Click | React 19 + Vite | `miniapp.umrabor.uz` |
| Backend API | FastAPI + PostgreSQL | `api.umrabor.uz` |

## Структура монорепо

```
apps/
  web/         публичный сайт (umrabor.uz)
  platform/    АРМ Платформы
  partner/     АРМ Партнёра
  miniapp/     Mini App в Click
services/
  api/         FastAPI backend
packages/
  ui/          общие React-компоненты
  shared/      общие типы, i18n, утилиты
  api-client/  TypeScript-клиент (генерируется из OpenAPI)
prototypes/    оригинальные HTML-прототипы (архив)
docs/          бриф + Q&A
infra/         Docker, Nginx, deploy
```

## Быстрый старт (dev)

Требования: Docker, Docker Compose, Node 20+, pnpm 9+, Python 3.12.

```bash
# 1. Поднять инфраструктуру (Postgres, Redis, MinIO)
make up

# 2. Установить зависимости и применить миграции
make install
make migrate
make seed   # demo-данные

# 3. Запустить backend + все фронты
make dev
```

После старта:
- API:        http://localhost:8000  · Swagger: http://localhost:8000/docs
- Сайт:       http://localhost:3000
- Платформа:  http://localhost:3001
- Партнёр:    http://localhost:3002
- Mini App:   http://localhost:3003
- MinIO:      http://localhost:9001 (admin / minioadmin)

## Демо-аккаунты

| Роль | Логин | Пароль |
| --- | --- | --- |
| Super-admin UMRABOR | `yulia.m` | `Demo-2026!` |
| Админ UMRABOR | `anvar.q` | `Demo-2026!` |
| Админ партнёра (Ramaz Travel) | `ibrahim.r` | `Demo-2026!` |
| Оператор партнёра | `dilfuza.t` | `Demo-2026!` |
| Клиент Mini App | `+998 90 123 4321` | OTP `0000` |

## Документация

- [UMRABOR_Full_Documentation.md](docs/UMRABOR_Full_Documentation.md) — продуктовый бриф + 230 Q&A
- [prototypes/](prototypes/) — оригинальные HTML-прототипы

## Деплой

См. `infra/scripts/deploy.sh` и `infra/nginx/`.
