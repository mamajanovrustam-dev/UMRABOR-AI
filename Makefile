.PHONY: help up down logs install install-api install-web migrate revision seed dev dev-api dev-web dev-platform dev-partner dev-miniapp test lint clean reset

help:
	@echo "UMRABOR — команды разработки"
	@echo ""
	@echo "  make up            — поднять Postgres, Redis, MinIO"
	@echo "  make down          — остановить инфраструктуру"
	@echo "  make logs          — логи docker"
	@echo "  make install       — установить все зависимости (api + web)"
	@echo "  make migrate       — применить миграции БД"
	@echo "  make revision m=.. — создать новую миграцию"
	@echo "  make seed          — загрузить demo-данные"
	@echo "  make dev           — запустить backend + все фронты (parallel)"
	@echo "  make dev-api       — только backend (FastAPI на :8000)"
	@echo "  make dev-web       — только публичный сайт (:3000)"
	@echo "  make dev-platform  — только АРМ Платформы (:3001)"
	@echo "  make dev-partner   — только АРМ Партнёра (:3002)"
	@echo "  make dev-miniapp   — только Mini App (:3003)"
	@echo "  make test          — все тесты"
	@echo "  make lint          — линт"
	@echo "  make reset         — снести БД и поднять заново"

up:
	docker compose up -d
	@echo "Ждём готовности Postgres..."
	@until docker exec umrabor_pg pg_isready -U umrabor -d umrabor > /dev/null 2>&1; do sleep 1; done
	@echo "✓ Инфраструктура готова."

down:
	docker compose down

logs:
	docker compose logs -f --tail=100

install: install-api install-web

install-api:
	cd services/api && python -m venv .venv && \
	. .venv/bin/activate && pip install --upgrade pip && pip install -e ".[dev]"

install-web:
	pnpm install

migrate:
	cd services/api && . .venv/bin/activate && alembic upgrade head

revision:
	cd services/api && . .venv/bin/activate && alembic revision --autogenerate -m "$(m)"

seed:
	cd services/api && . .venv/bin/activate && python -m app.scripts.seed

dev-api:
	cd services/api && . .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-web:
	pnpm --filter @umrabor/web dev

dev-platform:
	pnpm --filter @umrabor/platform dev

dev-partner:
	pnpm --filter @umrabor/partner dev

dev-miniapp:
	pnpm --filter @umrabor/miniapp dev

dev:
	pnpm dev

test:
	cd services/api && . .venv/bin/activate && pytest -v
	pnpm test

lint:
	cd services/api && . .venv/bin/activate && ruff check . && ruff format --check .
	pnpm lint

reset:
	docker compose down -v
	$(MAKE) up
	sleep 2
	$(MAKE) migrate
	$(MAKE) seed
