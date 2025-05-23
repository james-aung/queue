"""Tests for queue entry endpoints."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.queue import EntryStatus, Queue, QueueEntry, QueueStatus


class TestJoinQueue:
    """Test joining a queue."""

    def test_join_queue(self, client: TestClient, test_queue: Queue):
        """Test successfully joining a queue."""
        response = client.post(
            "/api/entries/join",
            json={
                "queue_id": test_queue.id,
                "customer_name": "John Doe",
                "phone_number": "+1234567890",
                "party_size": 2,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["customer_name"] == "John Doe"
        assert data["position"] == 1
        assert data["status"] == "waiting"
        assert data["estimated_wait_minutes"] == 0  # First in queue

    def test_join_queue_multiple(self, client: TestClient, test_queue: Queue):
        """Test multiple people joining queue."""
        # First person
        response = client.post(
            "/api/entries/join",
            json={
                "queue_id": test_queue.id,
                "customer_name": "First",
                "phone_number": "+1111111111",
                "party_size": 1,
            },
        )
        assert response.status_code == 200

        # Second person
        response = client.post(
            "/api/entries/join",
            json={
                "queue_id": test_queue.id,
                "customer_name": "Second",
                "phone_number": "+2222222222",
                "party_size": 1,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["position"] == 2
        assert data["estimated_wait_minutes"] == 5  # 1 person ahead × 5 min

    def test_join_nonexistent_queue(self, client: TestClient):
        """Test joining non-existent queue."""
        response = client.post(
            "/api/entries/join",
            json={
                "queue_id": 999,
                "customer_name": "John",
                "phone_number": "+1234567890",
                "party_size": 1,
            },
        )
        assert response.status_code == 404

    def test_join_closed_queue(
        self, client: TestClient, db: Session, test_queue: Queue
    ):
        """Test joining a closed queue."""
        test_queue.status = QueueStatus.CLOSED
        db.commit()

        response = client.post(
            "/api/entries/join",
            json={
                "queue_id": test_queue.id,
                "customer_name": "John",
                "phone_number": "+1234567890",
                "party_size": 1,
            },
        )
        assert response.status_code == 400
        assert "not accepting new entries" in response.json()["detail"]


class TestListQueueEntries:
    """Test listing queue entries."""

    def test_list_entries(self, client: TestClient, db: Session, test_queue: Queue):
        """Test listing entries in a queue."""
        # Add some entries
        for i in range(3):
            entry = QueueEntry(
                queue_id=test_queue.id,
                customer_name=f"Customer {i + 1}",
                phone_number=f"+123456789{i}",
                position=i + 1,
                status=EntryStatus.WAITING,
            )
            db.add(entry)
        db.commit()

        response = client.get(f"/api/entries/queue/{test_queue.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["customer_name"] == "Customer 1"
        assert data[0]["estimated_wait_minutes"] == 0
        assert data[1]["estimated_wait_minutes"] == 5
        assert data[2]["estimated_wait_minutes"] == 10

    def test_list_entries_with_status_filter(
        self, client: TestClient, db: Session, test_queue: Queue
    ):
        """Test listing entries with status filter."""
        # Add entries with different statuses
        waiting = QueueEntry(
            queue_id=test_queue.id,
            customer_name="Waiting",
            phone_number="+1111111111",
            position=1,
            status=EntryStatus.WAITING,
        )
        served = QueueEntry(
            queue_id=test_queue.id,
            customer_name="Served",
            phone_number="+2222222222",
            position=2,
            status=EntryStatus.SERVED,
        )
        db.add_all([waiting, served])
        db.commit()

        # Get only waiting entries
        response = client.get(f"/api/entries/queue/{test_queue.id}?status=waiting")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["customer_name"] == "Waiting"


class TestGetEntry:
    """Test getting a specific entry."""

    def test_get_entry(self, client: TestClient, db: Session, test_queue: Queue):
        """Test getting entry details."""
        entry = QueueEntry(
            queue_id=test_queue.id,
            customer_name="John Doe",
            phone_number="+1234567890",
            position=1,
            status=EntryStatus.WAITING,
        )
        db.add(entry)
        db.commit()

        response = client.get(f"/api/entries/{entry.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == entry.id
        assert data["customer_name"] == "John Doe"
        assert data["estimated_wait_minutes"] == 0

    def test_get_nonexistent_entry(self, client: TestClient):
        """Test getting non-existent entry."""
        response = client.get("/api/entries/999")
        assert response.status_code == 404


class TestCallEntry:
    """Test calling customers."""

    def test_call_entry(
        self,
        client: TestClient,
        db: Session,
        admin_auth_headers: dict[str, str],
        test_queue: Queue,
    ):
        """Test calling a customer."""
        entry = QueueEntry(
            queue_id=test_queue.id,
            customer_name="John Doe",
            phone_number="+1234567890",
            position=1,
            status=EntryStatus.WAITING,
        )
        db.add(entry)
        db.commit()

        response = client.patch(
            f"/api/entries/{entry.id}/call", headers=admin_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "called"
        assert data["called_at"] is not None

    def test_call_entry_non_admin(
        self,
        client: TestClient,
        db: Session,
        auth_headers: dict[str, str],
        test_queue: Queue,
    ):
        """Test calling entry as non-admin."""
        entry = QueueEntry(
            queue_id=test_queue.id,
            customer_name="John",
            phone_number="+1234567890",
            position=1,
            status=EntryStatus.WAITING,
        )
        db.add(entry)
        db.commit()

        response = client.patch(f"/api/entries/{entry.id}/call", headers=auth_headers)
        assert response.status_code == 403

    def test_call_already_called_entry(
        self,
        client: TestClient,
        db: Session,
        admin_auth_headers: dict[str, str],
        test_queue: Queue,
    ):
        """Test calling an already called entry."""
        entry = QueueEntry(
            queue_id=test_queue.id,
            customer_name="John",
            phone_number="+1234567890",
            position=1,
            status=EntryStatus.CALLED,
        )
        db.add(entry)
        db.commit()

        response = client.patch(
            f"/api/entries/{entry.id}/call", headers=admin_auth_headers
        )
        assert response.status_code == 400
        assert "already" in response.json()["detail"]


class TestServeEntry:
    """Test serving customers."""

    def test_serve_entry(
        self,
        client: TestClient,
        db: Session,
        admin_auth_headers: dict[str, str],
        test_queue: Queue,
    ):
        """Test marking customer as served."""
        entry = QueueEntry(
            queue_id=test_queue.id,
            customer_name="John",
            phone_number="+1234567890",
            position=1,
            status=EntryStatus.CALLED,
        )
        db.add(entry)
        db.commit()

        response = client.patch(
            f"/api/entries/{entry.id}/serve", headers=admin_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "served"
        assert data["served_at"] is not None


class TestCancelEntry:
    """Test cancelling entries."""

    def test_cancel_entry(self, client: TestClient, db: Session, test_queue: Queue):
        """Test cancelling an entry."""
        entry = QueueEntry(
            queue_id=test_queue.id,
            customer_name="John",
            phone_number="+1234567890",
            position=1,
            status=EntryStatus.WAITING,
        )
        db.add(entry)
        db.commit()

        response = client.patch(f"/api/entries/{entry.id}/cancel")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"

    def test_cancel_served_entry(
        self, client: TestClient, db: Session, test_queue: Queue
    ):
        """Test cancelling already served entry."""
        entry = QueueEntry(
            queue_id=test_queue.id,
            customer_name="John",
            phone_number="+1234567890",
            position=1,
            status=EntryStatus.SERVED,
        )
        db.add(entry)
        db.commit()

        response = client.patch(f"/api/entries/{entry.id}/cancel")
        assert response.status_code == 400
        assert "already" in response.json()["detail"]
