.PHONY: help install env-supabase lint format check test docker-build docker-run clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies (including dev)
	uv sync

env-supabase: ## Generate .env from Supabase CLI (run after: supabase start)
	@command -v supabase >/dev/null 2>&1 || { echo "Supabase CLI not found. Install: https://supabase.com/docs/guides/cli"; exit 1; }
	@command -v jq >/dev/null 2>&1 || { echo "jq required. Install jq, or run 'supabase status' and copy API URL, service_role key, and JWT secret into .env"; exit 1; }
	@if [ -f .env ]; then echo ".env already exists — delete it first to regenerate"; exit 1; fi
	@json=$$(supabase status --output json 2>/dev/null); \
	url=$$(echo "$$json" | jq -r '.APIUrl // .api_url // empty'); \
	key=$$(echo "$$json" | jq -r '.service_role_key // empty'); \
	jwt=$$(echo "$$json" | jq -r '.JWT_SECRET // .jwt_secret // empty'); \
	if [ -z "$$url" ] || [ -z "$$key" ] || [ -z "$$jwt" ]; then \
	  echo "Run 'supabase start' first, then try again. Or run 'supabase status' and set .env manually."; exit 1; \
	fi; \
	printf 'SUPABASE_URL=%s\nSUPABASE_SERVICE_ROLE_KEY=%s\nSUPABASE_JWT_SECRET=%s\n' "$$url" "$$key" "$$jwt" > .env; \
	echo "Created .env from supabase status"

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

# ── Docker ────────────────────────────────────────────────────────────

docker-build: ## Build the FastAPI app Docker image
	docker build -t fastapi-app .

docker-run: ## Run the FastAPI app image standalone 
	docker run --rm -p 8000:8000 --env-file .env fastapi-app

clean: ## Remove caches and build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov .coverage coverage.xml
