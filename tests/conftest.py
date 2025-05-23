"""Pytest configuration and fixtures."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies.database import get_db
from app.core.security import get_password_hash
from app.db.base import Base
from app.main import app
from app.models.queue import Queue
from app.models.user import User

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    """Override the get_db dependency for tests."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database override."""
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpass123"),
        phone_number="+1234567890",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_admin(db: Session) -> User:
    """Create a test admin user."""
    admin = User(
        email="admin@example.com",
        username="adminuser",
        hashed_password=get_password_hash("adminpass123"),
        phone_number="+0987654321",
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture
def test_queue(db: Session, test_admin: User) -> Queue:
    """Create a test queue with admin."""
    queue = Queue(
        name="test-queue",
        business_name="Test Business",
        description="Test queue description",
        address="123 Test St",
        estimated_wait_minutes=5,
    )
    db.add(queue)
    db.flush()

    # Add admin
    queue.admins.append(test_admin)
    db.commit()
    db.refresh(queue)
    return queue


@pytest.fixture
def auth_headers(client: TestClient, test_user: User) -> dict[str, str]:
    """Get authentication headers for test user."""
    response = client.post(
        "/api/auth/token",
        data={"username": test_user.username, "password": "testpass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(client: TestClient, test_admin: User) -> dict[str, str]:
    """Get authentication headers for test admin."""
    response = client.post(
        "/api/auth/token",
        data={"username": test_admin.username, "password": "adminpass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
