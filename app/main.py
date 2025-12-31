from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up AskDocs API...")
    # Startup tasks (connection checks, etc) will go here
    yield
    logger.info("Shutting down AskDocs API...")
    # Cleanup tasks

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

from app.api.v1.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify service status.
    TODO: Add DB and Redis ping.
    """
    return {"status": "ok", "app": settings.PROJECT_NAME}

@app.get("/")
async def root():
    return {"message": "Welcome to AskDocs API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
