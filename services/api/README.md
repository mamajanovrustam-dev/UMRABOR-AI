# UMRABOR API

Backend на FastAPI + SQLAlchemy 2 + PostgreSQL.

## Старт

```bash
# Из корня монорепо
make up         # поднять Postgres/Redis/MinIO
make install    # установить зависимости (создаст .venv)
make migrate    # применить миграции
make seed       # загрузить demo-данные
make dev-api    # запустить на :8000
```

Swagger: http://localhost:8000/docs

## Структура

```
app/
  main.py            FastAPI entrypoint, CORS, lifespan
  core/
    config.py        Pydantic Settings (env)
    security.py      JWT, bcrypt
  db/
    base.py          Base declarative class
    session.py       AsyncSession
  api/v1/            HTTP роутеры (по доменам)
  models/            SQLAlchemy ORM
  schemas/           Pydantic-схемы (request/response)
  services/          бизнес-логика
  utils/             хелперы
alembic/             миграции
scripts/             сиды, утилиты CLI
tests/               pytest
```

## Тесты

```bash
make test
```
