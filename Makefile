.PHONY: help install lint format check test docker-build docker-run docker-up docker-down clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies (including dev)
	uv sync

lint: ## Run linter (ruff check)
	uv run ruff check app tests

format: ## Format code (ruff format)
	uv run ruff format app tests
	uv run ruff check --fix app tests

check: ## Run linter + format check (CI-friendly, no auto-fix)
	uv run ruff check app tests
	uv run ruff format --check app tests

test: ## Run tests
	uv run pytest

docker-build: ## Build Docker image
	docker build -t fastapi-app .

docker-run: ## Run Docker container on port 8000
	docker run --rm -p 8000:8000 --env-file .env fastapi-app

docker-up: ## Start services via docker-compose (dev mode with reload)
	@test -f .env || (cp .env.example .env && echo "Created .env from .env.example")
	docker compose up --build

docker-down: ## Stop docker-compose services
	docker compose down

clean: ## Remove caches and build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov .coverage coverage.xml
