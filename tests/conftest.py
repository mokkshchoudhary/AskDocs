import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.db.base import Base
from app.main import app
from app.core.config import settings
from app.db.session import get_db

# Override DB URL for verification (optional, or use same local DB)
# For simplicity, we use the same dev DB but wrap in transaction or just clean up?
# Or use sqlite? Pgvector requires postgres.
# We will use the running docker postgres but maybe a separate DB?
# Keeping it simple: Use same DB, but careful.
# Ideally, we should create a test DB.
# For this task, we will just run against 'askdocs' DB assuming it's dev.

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

# TODO: Add DB fixtures if needed
