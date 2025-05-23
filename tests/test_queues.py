"""Tests for queue management endpoints."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.queue import Queue, QueueStatus
from app.models.user import User


class TestCreateQueue:
    """Test queue creation."""

    def test_create_queue(self, client: TestClient, auth_headers: dict[str, str]):
        """Test successful queue creation."""
        response = client.post(
            "/api/queues/",
            json={
                "name": "new-queue",
                "business_name": "New Business",
                "description": "A new queue",
                "address": "456 New St",
                "estimated_wait_minutes": 10,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "new-queue"
        assert data["business_name"] == "New Business"
        assert data["status"] == "active"
        assert data["current_size"] == 0
        assert len(data["admin_ids"]) == 1

    def test_create_duplicate_queue(
        self, client: TestClient, auth_headers: dict[str, str], test_queue: Queue
    ):
        """Test creating queue with duplicate name."""
        response = client.post(
            "/api/queues/",
            json={
                "name": test_queue.name,
                "business_name": "Another Business",
                "estimated_wait_minutes": 5,
            },
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_queue_unauthenticated(self, client: TestClient):
        """Test creating queue without authentication."""
        response = client.post(
            "/api/queues/",
            json={
                "name": "unauthorized-queue",
                "business_name": "Business",
                "estimated_wait_minutes": 5,
            },
        )
        assert response.status_code == 401


class TestListQueues:
    """Test queue listing."""

    def test_list_queues(self, client: TestClient, test_queue: Queue):
        """Test listing active queues."""
        response = client.get("/api/queues/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == test_queue.id
        assert data[0]["current_size"] == 0

    def test_list_queues_with_status_filter(
        self, client: TestClient, db: Session, test_queue: Queue
    ):
        """Test listing queues with status filter."""
        # Create a closed queue
        closed_queue = Queue(
            name="closed-queue",
            business_name="Closed Business",
            status=QueueStatus.CLOSED,
        )
        db.add(closed_queue)
        db.commit()

        # Get only active queues (default)
        response = client.get("/api/queues/")
        assert response.status_code == 200
        assert len(response.json()) == 1

        # Get closed queues
        response = client.get("/api/queues/?status=closed")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "closed-queue"


class TestGetQueue:
    """Test getting a specific queue."""

    def test_get_queue(self, client: TestClient, test_queue: Queue):
        """Test getting queue details."""
        response = client.get(f"/api/queues/{test_queue.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_queue.id
        assert data["name"] == test_queue.name
        assert data["current_size"] == 0
        assert len(data["admin_ids"]) == 1

    def test_get_nonexistent_queue(self, client: TestClient):
        """Test getting non-existent queue."""
        response = client.get("/api/queues/999")
        assert response.status_code == 404
        assert "Queue not found" in response.json()["detail"]


class TestUpdateQueue:
    """Test queue updates."""

    def test_update_queue_as_admin(
        self, client: TestClient, admin_auth_headers: dict[str, str], test_queue: Queue
    ):
        """Test updating queue as admin."""
        response = client.patch(
            f"/api/queues/{test_queue.id}",
            json={
                "description": "Updated description",
                "estimated_wait_minutes": 15,
                "status": "paused",
            },
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"
        assert data["estimated_wait_minutes"] == 15
        assert data["status"] == "paused"

    def test_update_queue_non_admin(
        self, client: TestClient, auth_headers: dict[str, str], test_queue: Queue
    ):
        """Test updating queue as non-admin."""
        response = client.patch(
            f"/api/queues/{test_queue.id}",
            json={"description": "Should fail"},
            headers=auth_headers,
        )
        assert response.status_code == 403
        assert "Not authorized" in response.json()["detail"]


class TestDeleteQueue:
    """Test queue deletion."""

    def test_delete_queue_as_admin(
        self, client: TestClient, admin_auth_headers: dict[str, str], test_queue: Queue
    ):
        """Test deleting queue as admin."""
        response = client.delete(
            f"/api/queues/{test_queue.id}", headers=admin_auth_headers
        )
        assert response.status_code == 204

        # Verify queue is deleted
        response = client.get(f"/api/queues/{test_queue.id}")
        assert response.status_code == 404

    def test_delete_queue_non_admin(
        self, client: TestClient, auth_headers: dict[str, str], test_queue: Queue
    ):
        """Test deleting queue as non-admin."""
        response = client.delete(f"/api/queues/{test_queue.id}", headers=auth_headers)
        assert response.status_code == 403


class TestQueueAdmins:
    """Test queue admin management."""

    def test_add_admin(
        self,
        client: TestClient,
        db: Session,
        admin_auth_headers: dict[str, str],
        test_queue: Queue,
        test_user: User,
    ):
        """Test adding an admin to queue."""
        response = client.post(
            f"/api/queues/{test_queue.id}/admins/{test_user.id}",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
        assert "successfully" in response.json()["message"]

        # Verify admin was added
        db.refresh(test_queue)
        assert len(test_queue.admins) == 2
        assert test_user in test_queue.admins

    def test_add_admin_non_admin(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        test_queue: Queue,
        test_admin: User,
    ):
        """Test adding admin as non-admin."""
        response = client.post(
            f"/api/queues/{test_queue.id}/admins/{test_admin.id}", headers=auth_headers
        )
        assert response.status_code == 403
