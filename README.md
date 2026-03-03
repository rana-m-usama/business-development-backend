# Business Development Backend

FastAPI REST API for job applications, platform profiles, documents, and user accounts. Uses **Supabase** (PostgreSQL + GoTrue) for database and auth.

You can run the app against **local Supabase** (Supabase CLI + Docker) or **remote Supabase** (hosted project).Only `.env` and how you run Supabase differ.

---

## Prerequisites

| For | You need |
|-----|----------|
| **Local Supabase** | [Docker](https://www.docker.com/products/docker-desktop/), [Supabase CLI](https://supabase.com/docs/guides/cli) |
| **Remote Supabase** | A [Supabase](https://supabase.com) project (API URL, keys from dashboard) |
| **App (either)** | [Python 3.12+](https://www.python.org/downloads/), [uv](https://docs.astral.sh/uv/) |

---

## Option A: Local Supabase (Supabase CLI)

Use this for development. Supabase runs in Docker; the app talks to it via `SUPABASE_URL` and keys from `supabase status`.

### 1. Start Supabase

```bash
supabase init    # only if you don’t have a supabase/ folder yet
supabase start   # starts Postgres, GoTrue, Studio, etc.
```

### 2. Create `.env` from local project

```bash
make env-supabase
```

Requires `jq`. If it fails, run `supabase status` and create `.env` manually with **API URL**, **service_role** key, and **JWT secret**.

### 3. Run the app

```bash
uv sync
uv run uvicorn app.main:app --reload
```

- **API:** [http://localhost:8000](http://localhost:8000)  
- **Docs:** [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)  
- **Supabase Studio:** [http://localhost:54323](http://localhost:54323)

To stop Supabase: `supabase stop`.  
Migrations in `supabase/migrations/` are applied on `supabase start` or `supabase db reset`.

---

## Option B: Remote Supabase (hosted project)

Use this to point at a Supabase project in the cloud (e.g. staging or production).

### 1. Get credentials from Supabase Dashboard

In your project: **Settings → API**. You need:

- **Project URL** → `SUPABASE_URL`
- **service_role** key (secret) → `SUPABASE_SERVICE_ROLE_KEY`
- **JWT Secret** (Settings → API → JWT Settings) → `SUPABASE_JWT_SECRET`

### 2. Create `.env`

Create a `.env` in the project root:

```env
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
SUPABASE_JWT_SECRET=your-jwt-secret
```

(Use the exact values from the dashboard.)

### 3. Run the app

```bash
uv sync
uv run uvicorn app.main:app --reload
```

- **API:** [http://localhost:8000](http://localhost:8000)  
- **Docs:** [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)

Apply migrations to the remote DB via Supabase CLI: `supabase db push` (with the project linked), or run SQL in the SQL Editor in the dashboard.

---

## Environment variables (same for local and remote)

The app reads these from `.env`:

| Variable | Where it comes from (local) | Where it comes from (remote) |
|----------|-----------------------------|-----------------------------|
| `SUPABASE_URL` | `supabase status` → API URL | Dashboard → Settings → API → Project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | `supabase status` → service_role key | Dashboard → Settings → API → service_role |
| `SUPABASE_JWT_SECRET` | `supabase status` → JWT secret | Dashboard → Settings → API → JWT Secret |

---

## Running the app in Docker

Works with **either** local or remote Supabase. Ensure `.env` exists and is correct, then:

```bash
docker compose up --build
```

The container uses `env_file: .env`, so it uses the same Supabase backend as when you run uvicorn on the host.

---

## Tech stack

- **FastAPI** · **PostgreSQL (Supabase)** · **GoTrue (JWT auth)** · **uv** · **Ruff** · **Pytest**

---

## Make commands

| Command | Description |
|--------|-------------|
| `make env-supabase` | Generate `.env` from `supabase status` (local only) |
| `make install` | Install dependencies |
| `make lint` | Run Ruff linter |
| `make format` | Format with Ruff |
| `make test` | Run tests |
| `make docker-build` | Build app Docker image |
| `make docker-run` | Run app image with `.env` |
| `make help` | List commands |

---

## Project structure

```
app/                    # FastAPI app (routes, services, schemas, auth)
supabase/
  migrations/           # SQL migrations (Supabase CLI or dashboard)
```

---

## Code quality

```bash
make lint
make format
```
