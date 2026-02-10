# CLAUDE.md — Design & Patterns for AI

This file documents the stack, patterns, and conventions so Claude (or any AI assistant) follows the same choices when adding features.

## Stack Summary

- **Package manager**: uv (fast, lockfile-based; `uv sync`, `uv add`, `uv run`)
- **App**: FastAPI 0.115+ (async, OpenAPI, dependency injection)
- **Server**: Uvicorn (ASGI)
- **Database**: PostgreSQL 16 (Alpine in Docker)
- **ORM**: SQLAlchemy 2.0 (async: `AsyncEngine`, `AsyncSession`)
- **Driver**: asyncpg (native async Postgres)
- **Cache**: Redis 7 (Alpine in Docker)
- **Redis client**: redis (with asyncio: `redis.asyncio.Redis`)
- **Config**: pydantic-settings (env vars, validation)
- **Tests**: pytest, pytest-asyncio, httpx (async tests, `AsyncClient`)
- **Linting**: black, isort, pylint, pyright (all configured in `pyproject.toml`)
- **Pre-commit**: hooks for black, isort, pylint, pyright
- **CI**: GitHub Actions (runs all checks on push/PR)

## Where to Add What

| What | Where | Notes |
|------|-------|-------|
| New API routes | `app/api/v1/` | Create a new file (e.g. `users.py`), add router to `app/api/v1/router.py` |
| New DB tables | `app/models/` | SQLAlchemy models; inherit from `Base` in `app/db/base.py` |
| New DTOs/contracts | `app/schemas/` | Pydantic models for request/response |
| Business logic | `app/services/` (optional folder) or inside routers if trivial | Keep routers thin |
| Config | `app/config.py` and `.env.example` | Add new env vars to `Settings` class |

## Conventions

- **Async everywhere**: All routes, DB queries, Redis ops are `async def`.
- **Dependency injection**: Use `Depends(get_db)` for DB sessions, `Depends(get_redis)` for Redis.
- **Return Pydantic models**: Routes return Pydantic schemas (FastAPI serializes to JSON).
- **Keep routers thin**: Move complex logic to service functions or modules.
- **Type hints**: Use strict type hints everywhere (pyright in strict mode).

## Dependencies

- **Adding deps**: `uv add <package>` (runtime) or `uv add --dev <package>` (dev).
- **After editing `pyproject.toml`**: run `uv sync`.
- **No duplicate version specifiers**: All versions in `pyproject.toml`.

## Testing

- **Framework**: pytest + pytest-asyncio
- **Structure**: tests in `tests/` mirroring `app/` (e.g. `tests/api/test_health.py`)
- **Fixtures**: Use `conftest.py` for shared fixtures (app, async HTTP client, DB session, Redis)
- **Run**: `uv run pytest tests/ -v`

## Docker

- **Hostnames**: App talks to `postgres` and `redis` (service names in docker-compose).
- **Run**: `docker compose up --build`
- **Tests**: Run inside container or with overrides for DB/Redis (mocks for unit tests).

## Common Tasks

### Add a new API endpoint

1. Create `app/api/v1/myfeature.py` with a router and routes
2. In `app/api/v1/router.py`, import and `api_router.include_router(myfeature.router)`
3. Add tests in `tests/api/test_myfeature.py`

### Add a new DB table

1. Create model in `app/models/mymodel.py` (inherit from `Base`)
2. Import in `app/models/__init__.py` so it's discovered
3. Tables auto-create on app startup (or use Alembic for migrations later)

### Add a new dependency

```bash
uv add <package>
uv sync
```

For dev-only (linting, testing):
```bash
uv add --dev <package>
uv sync
```

### Run all checks locally (before committing)

```bash
uv run black .
uv run isort .
uv run pylint app/
uv run pyright
uv run pytest tests/ -v
```

Or use pre-commit:
```bash
uv run pre-commit run --all-files
```
