"""FastAPI application and lifespan."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from starlette.status import HTTP_404_NOT_FOUND, HTTP_303_SEE_OTHER

from app.api.v1.router import get_router
from app.config import get_settings
from app.db.base import Base
from app.db.session import get_db
from app.services.link_service import get_link_by_short_code, record_click
from app.services.fraud_service import validate_click


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncIterator[None]:
    """Startup: engine and session factory on app.state. Shutdown: dispose engine."""
    settings = get_settings()
    engine = create_async_engine(
        settings.database_url,
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )
    fastapi_app.state.engine = engine
    fastapi_app.state.async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="fiverr-interview",
    description="FastAPI skeleton with Postgres and Redis.",
    lifespan=lifespan,
)

app.include_router(get_router(), prefix="/api/v1")

# Debug: Print all routes
print("REGISTERED ROUTES:")
for route in app.routes:
    print(f"Route: {route.path}, Methods: {route.methods}, Name: {route.name}")


@app.get("/")
async def root() -> dict[str, str]:
    """Root: simple OK message."""
    return {"message": "URL Shortener API is running"}


@app.get("/{short_code}")
async def redirect_to_original_url(
    short_code: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Redirect a short link to its original URL.
    Records the click and validates it for fraud.
    """
    # Skip API routes to prevent conflict with API endpoints
    if short_code.startswith("api"):
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Not found"
        )

    link = await get_link_by_short_code(db, short_code)
    if not link:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Short link not found"
        )

    # Get IP and user agent for fraud check
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    # Perform fraud validation (takes 100ms as per requirement)
    is_valid = await validate_click(ip_address, user_agent)

    # Record the click
    await record_click(db, link.id, ip_address, user_agent, is_valid)

    # Redirect to original URL
    return RedirectResponse(url=link.original_url, status_code=HTTP_303_SEE_OTHER)
