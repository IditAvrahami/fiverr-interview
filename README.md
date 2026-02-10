# fiverr-interview

FastAPI skeleton with Postgres, Redis, Docker, uv, lint/tests.

## Prerequisites

- **Docker** and **Docker Compose** (for running all services)
- For local dev: **Python 3.12+**, **[uv](https://docs.astral.sh/uv/getting-started/installation)**, **Git**

## Overall Design

This is a production-style FastAPI skeleton with:
- **API**: FastAPI with async endpoints
- **Database**: PostgreSQL 16 (async SQLAlchemy + asyncpg)
- **Cache**: Redis 7
- **Package manager**: uv (fast, lockfile-based)
- **Code quality**: black, isort, pylint, pyright, pre-commit
- **Testing**: pytest with async support
- **CI**: GitHub Actions running all checks

**Directory layout**:
```
app/             # FastAPI application
  main.py        # App entry, lifespan
  config.py      # Pydantic settings (env vars)
  api/v1/        # API routes (health checks)
  db/            # Database session, base
  redis_client.py # Redis connection
  models/        # SQLAlchemy models (empty - add yours)
  schemas/       # Pydantic schemas (empty - add yours)
tests/           # pytest tests
docker-compose.yml  # All services (app, postgres, redis)
```

**Config**: Loaded from `.env` file and environment variables via `pydantic-settings`. Docker uses hostnames `postgres` and `redis`.

## How to Run

### Option A: Docker (recommended)

```bash
docker compose up --build
```

- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### Test that the server runs (cURL)

Basic liveness:
```bash
curl -s http://localhost:8000/api/v1/health
```

Check Postgres connectivity:
```bash
curl -s http://localhost:8000/api/v1/health/db
```

Check Redis connectivity:
```bash
curl -s http://localhost:8000/api/v1/health/redis
```

All health checks (verbose):
```bash
curl -s -w "\n%{http_code}\n" http://localhost:8000/api/v1/health
curl -s -w "\n%{http_code}\n" http://localhost:8000/api/v1/health/db
curl -s -w "\n%{http_code}\n" http://localhost:8000/api/v1/health/redis
```

### Option B: Local Development

1. Install uv (if not already): see [uv installation](https://docs.astral.sh/uv/getting-started/installation)
2. Install dependencies:
   ```bash
   uv sync
   ```
3. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
4. Start Postgres and Redis:
   ```bash
   docker compose up -d postgres redis
   ```
5. Run the app:
   ```bash
   uv run uvicorn app.main:app --reload
   ```
6. In VS Code: select `.venv/Scripts/python.exe` (Windows) or `.venv/bin/python` (Mac/Linux) as interpreter

## Tests

Run all tests:
```bash
uv run pytest tests/ -v
```

Run with coverage:
```bash
uv run pytest tests/ -v --cov=app --cov-report=html
```

Run specific test file:
```bash
uv run pytest tests/api/test_health.py -v
```

## Lint / Type-check

Check only (no changes):
```bash
uv run black --check .
uv run isort --check .
uv run pylint app/
uv run pyright
```

Auto-fix formatting:
```bash
uv run black .
uv run isort .
```

## Pre-commit

Install hooks:
```bash
uv run pre-commit install
```

Run all hooks:
```bash
uv run pre-commit run --all-files
```

## Docker Commands

View logs (all services):
```bash
docker compose logs -f
```

View logs (specific service):
```bash
docker compose logs -f app
docker compose logs -f postgres
docker compose logs -f redis
```

Stop all services:
```bash
docker compose down
```

Stop and remove volumes (clean slate):
```bash
docker compose down -v
```

Rebuild and restart:
```bash
docker compose up --build --force-recreate
```

## Database & Redis Access

Access PostgreSQL:
```bash
docker compose exec postgres psql -U user -d dbname
```

Access Redis CLI:
```bash
docker compose exec redis redis-cli
```

## CI

On every push/PR, GitHub Actions runs the same checks: black, isort, pylint, pyright, and pytest.

See [.github/workflows/ci.yml](.github/workflows/ci.yml).

## Links

- **Extending the app**: See [CLAUDE.md](CLAUDE.md) for stack, patterns, and where to add code.
- **Claude Code setup**: See [docs/CLAUDE_CODE_SETUP.md](docs/CLAUDE_CODE_SETUP.md) for configuring the Claude Code extension in VS Code with AWS Bedrock API key.
