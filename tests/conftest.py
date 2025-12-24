"""Shared test fixtures for AI Service tests."""
import pytest
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.db.base_class import Base
from app.db.session import get_db
from app.core.config import settings
from app.core.security import create_access_token

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create async engine for testing
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
)

TestingSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database override."""
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers() -> dict:
    """Create authentication headers for test requests."""
    access_token = create_access_token(subject="test-user-id")
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def mock_abacus_client(monkeypatch):
    """Mock Abacus.AI client for testing."""
    class MockAbacusClient:
        async def generate_text(self, prompt: str, **kwargs) -> str:
            return f"Generated: {prompt[:50]}"

        async def translate_text(self, text: str, target_language: str, **kwargs) -> str:
            return f"[{target_language.upper()}] {text}"

        async def enhance_content(self, content: str, enhancement_type: str, **kwargs) -> str:
            return f"Enhanced ({enhancement_type}): {content}"

        async def generate_image(self, prompt: str, **kwargs) -> str:
            return "https://images.unsplash.com/photo-1726758267577-f8ca9449ed6b?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxmZWF0dXJlZC1waG90b3MtZmVlZHw2NHx8fGVufDB8fHx8fA%3D%3D"

    mock_client = MockAbacusClient()
    monkeypatch.setattr("app.core.abacus_client.AbacusAIClient._instance", mock_client)
    return mock_client
