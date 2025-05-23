"""Tests for authentication endpoints."""

from fastapi.testclient import TestClient

from app.models.user import User


class TestRegistration:
    """Test user registration."""

    def test_register_user(self, client: TestClient):
        """Test successful user registration."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "newpass123",
                "phone_number": "+1234567890",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert "password" not in data
        assert "hashed_password" not in data

    def test_register_duplicate_email(self, client: TestClient, test_user: User):
        """Test registration with duplicate email."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": test_user.email,
                "username": "different",
                "password": "pass123",
            },
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_register_duplicate_username(self, client: TestClient, test_user: User):
        """Test registration with duplicate username."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "different@example.com",
                "username": test_user.username,
                "password": "pass123",
            },
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]


class TestLogin:
    """Test user login."""

    def test_login_success(self, client: TestClient, test_user: User):
        """Test successful login."""
        response = client.post(
            "/api/auth/token",
            data={"username": test_user.username, "password": "testpass123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client: TestClient, test_user: User):
        """Test login with wrong password."""
        response = client.post(
            "/api/auth/token",
            data={"username": test_user.username, "password": "wrongpass"},
        )
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent user."""
        response = client.post(
            "/api/auth/token", data={"username": "nonexistent", "password": "pass123"}
        )
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]


class TestAuthentication:
    """Test authentication requirements."""

    def test_access_protected_endpoint_without_token(self, client: TestClient):
        """Test accessing protected endpoint without token."""
        response = client.post("/api/queues/", json={})
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_access_protected_endpoint_with_invalid_token(self, client: TestClient):
        """Test accessing protected endpoint with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.post("/api/queues/", json={}, headers=headers)
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]

    def test_access_protected_endpoint_with_valid_token(
        self, client: TestClient, auth_headers: dict[str, str]
    ):
        """Test accessing protected endpoint with valid token."""
        response = client.post(
            "/api/queues/",
            json={
                "name": "test-queue-auth",
                "business_name": "Test Business",
                "estimated_wait_minutes": 5,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
