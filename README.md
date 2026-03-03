# Business Development Backend

FastAPI app. Python 3.12+, [uv](https://docs.astral.sh/uv/) for deps.

## Setup

```bash
uv sync
cp .env.example .env
```

Edit `.env` and fill in your **Supabase** credentials (`SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`).
Get them from [Supabase Dashboard → Project Settings → API](https://supabase.com/dashboard).

## Database Migrations

Migration files live in `supabase/migrations/`. To apply them:

** Supabase CLI:**

```bash
# Install CLI (macOS)
brew install supabase/tap/supabase

# Login (opens browser to generate an access token)
supabase login

# Link to your remote project
supabase link --project-ref <your-project-ref>

# Push migrations
supabase db push
```

## Running Locally

```bash
uv run uvicorn app.main:app --reload
```

API at http://127.0.0.1:8000 — docs at `/api/v1/docs`.

## Docker

**Build & run:**

```bash
docker build -t fastapi-app . && docker run -p 8000:8000 fastapi-app
```

**Dev mode (with hot-reload via docker-compose):**

```bash
docker compose up --build
```

## Linting & Formatting

```bash
make lint        # Run ruff linter
make format      # Auto-format code + fix lint issues
make check       # CI-friendly check (no auto-fix)
```

## Tests

```bash
make test        # or: uv run pytest
```

## All Make Commands

```bash
make help        # Show all available commands
```
