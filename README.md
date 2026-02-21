# Business Development Backend

FastAPI app. Python 3.12+, [uv](https://docs.astral.sh/uv/) for deps.

**Setup**

```bash
uv sync
cp .env.example .env
```

**Run**

```bash
uv run uvicorn app.main:app --reload
```

API at http://127.0.0.1:8000 — docs at `/api/v1/docs`.

**Other**

- Tests: `uv run pytest`
- Lint: `uv run pylint app`
