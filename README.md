# Business Development Backend

FastAPI REST API for job applications, platform profiles, documents, and user accounts. Uses **Supabase** (PostgreSQL + GoTrue) for database and auth.

You can run the app against **local Supabase** (Supabase CLI + Docker) or **remote Supabase** (hosted project). Only `.env` and how you run Supabase differ.

---

## Prerequisites

| For | You need |
|-----|----------|
| **Local Supabase** | [Docker Desktop](https://docs.docker.com/desktop/) (must be **running**), [Supabase CLI](https://supabase.com/docs/guides/cli) |
| **Remote Supabase** | A [Supabase](https://supabase.com) project (API URL, keys from dashboard) |
| **App (either)** | [Python 3.12+](https://www.python.org/downloads/), [uv](https://docs.astral.sh/uv/) |

**Local development:** Before running `supabase start`, ensure **Docker Desktop is running**. If you see `Cannot connect to the Docker daemon`, start Docker Desktop and wait until it is fully up, then run `supabase start` again.

---

## Option A: Local Supabase (Supabase CLI)

Use this for development. Supabase runs in Docker; the app talks to it via `SUPABASE_URL` and keys from `supabase status`.

### 1. Start Docker and Supabase

Ensure **Docker Desktop is running**, then:

```bash
supabase init    # only if you don’t have a supabase/ folder yet
supabase start   # starts Postgres, GoTrue, Studio, etc.
```

If `supabase start` fails with a Docker connection error, start Docker Desktop and retry.

### 2. Create `.env` from local project

```bash
make env-supabase
```

Requires `jq`. If it fails, run `supabase status --output json` and set `.env` from `API_URL`, `SERVICE_ROLE_KEY`, and `JWT_SECRET`.

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

Optional: in `supabase/config.toml` you can set `[auth]` → `jwt_expiry` (seconds) to control access token lifetime; restart Supabase after changes.

---

## Auth (first user and admin)

- **First admin:** When the DB has no users, call **POST** `/api/v1/auth/bootstrap` (no auth) with `first_name`, `last_name`, `email`, `password`. Creates the first admin.
- **Login:** **POST** `/api/v1/auth/login` with `email` and `password`; use the returned `access_token` as Bearer token for protected endpoints.
- **Admin add users:** An admin can create more users (including other admins) via **POST** `/api/v1/auth/admin/users` with Bearer token and body: `first_name`, `last_name`, `email`, `password`, `role` (`admin` | `bd` | `developer`).

Full API: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs).

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

The container uses `env_file: .env`. When using **local** Supabase, `SUPABASE_URL` is overridden to `http://host.docker.internal:54321` inside the container so the app can reach Supabase on the host.

---

## Tech stack

- **FastAPI** · **PostgreSQL (Supabase)** · **GoTrue (JWT auth)** · **uv** · **Ruff** · **Pytest**

---

## Make commands

| Command | Description |
|--------|-------------|
| `make help` | List all commands |
| `make install` | Install dependencies (`uv sync`) |
| `make env-supabase` | Generate `.env` from `supabase status` (local only; run after `supabase start`) |
| `make lint` | Run Ruff linter |
| `make format` | Format code and run Ruff with auto-fix |
| `make check` | Lint + format check only (no changes; CI-friendly) |
| `make test` | Run pytest |
| `make docker-build` | Build app Docker image |
| `make docker-run` | Run app container with `.env` |
| `make clean` | Remove caches and coverage artifacts |

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
make format    # format and fix
make check     # verify lint + format
make test      # run tests
```
