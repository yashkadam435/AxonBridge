"""
AxonBridge — Test Configuration

Shared fixtures for async testing with isolated database transactions.
"""

import asyncio
import uuid
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.core.database import Base, get_db_session
from app.core.security import create_access_token, hash_password
from app.main import create_app
from app.models.role import DEFAULT_PERMISSIONS, DEFAULT_ROLES, Permission, Role, RolePermission, UserRole
from app.models.tenant import Tenant
from app.models.user import User

settings = get_settings()

# Use a test database URL
TEST_DATABASE_URL = settings.DATABASE_URL.replace("/axonbridge", "/axonbridge_test")

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionFactory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def setup_database():
    """Create all tables at session start, drop at session end."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(setup_database) -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional database session that rolls back after each test."""
    async with TestSessionFactory() as session:
        async with session.begin():
            yield session
            await session.rollback()


@pytest_asyncio.fixture
async def app(db_session: AsyncSession):
    """Create a test application with overridden DB dependency."""
    test_app = create_app()

    async def override_db():
        yield db_session

    test_app.dependency_overrides[get_db_session] = override_db
    return test_app


@pytest_asyncio.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    """HTTP test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def test_tenant(db_session: AsyncSession) -> Tenant:
    """Create a test tenant."""
    tenant = Tenant(
        name="Test Hospital",
        slug=f"test-hospital-{uuid.uuid4().hex[:8]}",
        description="Test tenant for unit tests",
        compliance_region="us",
        subscription_tier="enterprise",
        admin_email="admin@test-hospital.org",
    )
    db_session.add(tenant)
    await db_session.flush()
    return tenant


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession, test_tenant: Tenant) -> User:
    """Create a test user with admin role."""
    user = User(
        tenant_id=test_tenant.id,
        email=f"test-{uuid.uuid4().hex[:8]}@test-hospital.org",
        full_name="Test Admin User",
        hashed_password=hash_password("TestPassword123!"),
        title="System Administrator",
        department="IT",
        is_active=True,
        password_changed_at=datetime.now(UTC),
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def auth_headers(test_user: User, test_tenant: Tenant) -> dict[str, str]:
    """Generate JWT auth headers for the test user."""
    token = create_access_token(
        subject=str(test_user.id),
        tenant_id=str(test_tenant.id),
        roles=["system_admin"],
    )
    return {"Authorization": f"Bearer {token}"}
