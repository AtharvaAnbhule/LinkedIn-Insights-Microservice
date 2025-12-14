from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import database
from app.core.cache import cache
from app.core.logging_config import setup_logging
from app.api.v1 import pages


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    setup_logging()
    await database.connect()
    await cache.connect()

    yield

    # Shutdown
    await database.disconnect()
    await cache.disconnect()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="LinkedIn Insights Microservice - Production-ready backend for LinkedIn data analysis",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(pages.router, prefix="/api/v1", tags=["pages"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = await database.ping()
    cache_status = await cache.ping()

    return {
        "status": "healthy" if db_status and cache_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
        "cache": "connected" if cache_status else "disconnected"
    }
