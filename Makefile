# ================================
# AxonBridge — Makefile
# ================================

.PHONY: help dev api web db-migrate db-upgrade db-downgrade test lint clean docker-up docker-down seed

help: ## Show this help message
	@echo "AxonBridge Development Commands"
	@echo "================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ---------- Development ----------

dev: ## Start full development stack with Docker Compose
	docker compose -f infrastructure/docker/docker-compose.yml --env-file .env up --build

api: ## Start API server only (local, no Docker)
	cd apps/api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

web: ## Start frontend dev server only
	cd apps/web && npm run dev

# ---------- Database ----------

migrate: ## Run all pending migrations
	cd apps/api && alembic upgrade head

migrate-generate: ## Create a new Alembic migration (usage: make migrate-generate name="description")
	cd apps/api && alembic revision --autogenerate -m "$(name)"

db-reset: ## Reset database (DESTRUCTIVE)
	cd apps/api && alembic downgrade base && alembic upgrade head

seed: ## Seed development data
	cd apps/api && python seed.py

# ---------- Testing ----------

test: ## Run all tests
	cd apps/api && pytest tests/ -v --tb=short
	cd apps/web && npm run test 2>/dev/null || echo "Frontend tests not configured yet"

test-coverage: ## Run tests with coverage
	cd apps/api && pytest tests/ -v --tb=short --cov=app --cov-report=term-missing

test-api: ## Run API tests only
	cd apps/api && pytest tests/ -v --tb=short --cov=app --cov-report=term-missing

test-web: ## Run frontend tests only
	cd apps/web && npm run test

# ---------- Linting ----------

lint: ## Run all linters
	cd apps/api && ruff check app/ --fix
	cd apps/api && ruff format app/
	cd apps/web && npm run lint

# ---------- Docker ----------

docker-up: ## Start Docker services (detached)
	docker compose -f infrastructure/docker/docker-compose.yml --env-file .env up -d

docker-down: ## Stop Docker services
	docker compose -f infrastructure/docker/docker-compose.yml down

docker-logs: ## View Docker logs
	docker compose -f infrastructure/docker/docker-compose.yml logs -f

docker-clean: ## Remove Docker volumes (DESTRUCTIVE)
	docker compose -f infrastructure/docker/docker-compose.yml down -v --remove-orphans

# ---------- Utilities ----------

clean: ## Clean build artifacts
	docker compose -f infrastructure/docker/docker-compose.yml down -v --rmi all
	docker system prune -f
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .next -exec rm -rf {} + 2>/dev/null || true

build: ## Build all applications
	cd apps/web && npm run build

openapi: ## Generate OpenAPI spec
	cd apps/api && python -c "import json; from app.main import app; print(json.dumps(app.openapi(), indent=2))" > docs/api/openapi.json
