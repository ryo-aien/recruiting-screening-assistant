import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.routes import api_router
from app.config import get_settings
from app.core.database import AsyncSessionLocal

settings = get_settings()


async def check_and_seed_data():
    """Check if data exists and seed if in development environment."""
    if not settings.is_development:
        print("Environment: production - skipping seed data")
        return

    print("Environment: development - checking seed data...")

    async with AsyncSessionLocal() as session:
        # Check if jobs already exist
        result = await session.execute(text("SELECT COUNT(*) as cnt FROM jobs"))
        row = result.fetchone()
        if row and row[0] > 0:
            print(f"Seed data already exists ({row[0]} jobs) - skipping")
            return

    # Import and run seed
    print("No data found - seeding test data...")
    from app.seed import seed_data
    await seed_data()
    print("Seed data completed!")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    try:
        await check_and_seed_data()
    except Exception as e:
        print(f"Warning: Failed to seed data: {e}")
        if settings.debug:
            traceback.print_exc()
    yield
    # Shutdown


app = FastAPI(
    title="Recruitment Screening API",
    description="API for AI-powered recruitment document screening",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)


# Global exception handler for debugging
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Return detailed error info for debugging."""
    error_detail = {
        "detail": str(exc),
        "type": type(exc).__name__,
        "traceback": traceback.format_exc() if settings.debug else None,
    }
    print(f"Error: {type(exc).__name__}: {exc}")
    print(traceback.format_exc())
    return JSONResponse(status_code=500, content=error_detail)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
