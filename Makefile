# =============================================================================
# ContribHub — Developer Makefile
# =============================================================================
# Usage:
#   make setup      Install all dependencies (Node + Python)
#   make dev        Start all dev servers via Turborepo
#   make docker-up  Start Postgres and Redis containers
#   make test       Run all test suites
#   make lint       Lint all packages
#   make build      Build all packages for production
# =============================================================================

.PHONY: setup dev docker-up docker-down migrate test lint build format clean help

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

setup: ## Install all dependencies (Node + Python)
	npm install
	cd apps/api && pip install -r requirements.txt
	cd packages/ml-pipeline && pip install -e ".[dev]"
	@echo ""
	@echo "Setup complete. Copy .env.example to .env and fill in values."
	@echo "Then run 'make docker-up' to start Postgres and Redis."

# ---------------------------------------------------------------------------
# Development
# ---------------------------------------------------------------------------

dev: ## Start all dev servers via Turborepo
	npx turbo run dev

dev-web: ## Start only the web frontend
	cd apps/web && npm run dev

dev-api: ## Start only the API server
	cd apps/api && uvicorn app.main:app --reload --port 8000

# ---------------------------------------------------------------------------
# Docker
# ---------------------------------------------------------------------------

docker-up: ## Start Postgres and Redis containers
	docker compose up -d postgres redis

docker-down: ## Stop all Docker containers
	docker compose down

docker-up-all: ## Start all services (API, worker, Postgres, Redis)
	docker compose up -d

docker-logs: ## Tail logs from all containers
	docker compose logs -f

docker-reset: ## Stop containers and remove volumes
	docker compose down -v

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

migrate: ## Run database migrations to latest
	cd apps/api && alembic upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create MSG="add users table")
	cd apps/api && alembic revision --autogenerate -m "$(MSG)"

migrate-rollback: ## Rollback the last migration
	cd apps/api && alembic downgrade -1

# ---------------------------------------------------------------------------
# Testing
# ---------------------------------------------------------------------------

test: ## Run all test suites
	npx turbo run test
	cd apps/api && python -m pytest --tb=short
	cd packages/ml-pipeline && python -m pytest --tb=short

test-web: ## Run frontend tests
	cd apps/web && npm test -- --passWithNoTests

test-api: ## Run API tests
	cd apps/api && python -m pytest --tb=short -v

test-api-cov: ## Run API tests with coverage report
	cd apps/api && python -m pytest --tb=short --cov=app --cov-report=term-missing

test-ml: ## Run ML pipeline tests
	cd packages/ml-pipeline && python -m pytest --tb=short -v

test-integration: ## Run only integration tests (requires Docker services)
	cd apps/api && python -m pytest --tb=short -m integration

# ---------------------------------------------------------------------------
# Linting & Formatting
# ---------------------------------------------------------------------------

lint: ## Lint all packages
	npx turbo run lint
	cd apps/api && ruff check .
	cd packages/ml-pipeline && ruff check .

lint-fix: ## Auto-fix lint issues
	npx turbo run lint -- --fix
	cd apps/api && ruff check --fix .
	cd packages/ml-pipeline && ruff check --fix .

format: ## Format all code
	npx prettier --write .
	cd apps/api && ruff format .
	cd packages/ml-pipeline && ruff format .

format-check: ## Check formatting without modifying files
	npx prettier --check .
	cd apps/api && ruff format --check .
	cd packages/ml-pipeline && ruff format --check .

# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

build: ## Build all packages for production
	npx turbo run build

build-web: ## Build only the web frontend
	npx turbo run build --filter=@contribhub/web

build-docker: ## Build Docker images for API and web
	docker compose build api
	cd apps/web && docker build -t contribhub-web .

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

clean: ## Remove build artifacts and caches
	rm -rf apps/web/.next apps/web/out
	rm -rf packages/shared/dist
	rm -rf packages/github-action/dist
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -prune -exec rm -rf {} + 2>/dev/null || true

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
