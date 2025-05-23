"""Tests for SMS integration with API endpoints."""

from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.queue import EntryStatus, Queue, QueueEntry
from app.services.sms import MockSMSProvider, sms_service


class TestSMSIntegration:
    """Test SMS notifications in API endpoints."""

    def test_sms_sent_when_joining_queue(self, client: TestClient, test_queue: Queue):
        """Test SMS is sent when customer joins queue."""
        # Use mock provider
        mock_provider = MockSMSProvider()
        with patch.object(sms_service, "provider", mock_provider):
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

            # Check SMS was sent
            messages = mock_provider.get_sent_messages()
            assert len(messages) == 1
            assert messages[0]["to"] == "+1234567890"
            assert test_queue.business_name in messages[0]["body"]
            assert "position 1" in messages[0]["body"]

    def test_sms_sent_when_customer_called(
        self,
        client: TestClient,
        db: Session,
        admin_auth_headers: dict[str, str],
        test_queue: Queue,
    ):
        """Test SMS is sent when customer is called."""
        # Create entry
        entry = QueueEntry(
            queue_id=test_queue.id,
            customer_name="Jane Doe",
            phone_number="+0987654321",
            position=1,
            status=EntryStatus.WAITING,
        )
        db.add(entry)
        db.commit()

        # Use mock provider
        mock_provider = MockSMSProvider()
        with patch.object(sms_service, "provider", mock_provider):
            response = client.patch(
                f"/api/entries/{entry.id}/call", headers=admin_auth_headers
            )

            assert response.status_code == 200

            # Check SMS was sent
            messages = mock_provider.get_sent_messages()
            assert len(messages) == 1
            assert messages[0]["to"] == "+0987654321"
            assert "ready" in messages[0]["body"].lower()
            assert test_queue.business_name in messages[0]["body"]

    def test_no_sms_for_invalid_phone(self, client: TestClient, test_queue: Queue):
        """Test no SMS is sent for invalid phone numbers."""
        mock_provider = MockSMSProvider()
        with patch.object(sms_service, "provider", mock_provider):
            response = client.post(
                "/api/entries/join",
                json={
                    "queue_id": test_queue.id,
                    "customer_name": "Bad Phone",
                    "phone_number": "not-a-phone",
                    "party_size": 1,
                },
            )

            # Entry should still be created
            assert response.status_code == 200

            # But no SMS sent
            messages = mock_provider.get_sent_messages()
            assert len(messages) == 0

    def test_position_update_notification(
        self,
        client: TestClient,
        db: Session,
        admin_auth_headers: dict[str, str],
        test_queue: Queue,
    ):
        """Test SMS when position changes (e.g., someone ahead leaves)."""
        # Create two entries
        entry1 = QueueEntry(
            queue_id=test_queue.id,
            customer_name="First",
            phone_number="+1111111111",
            position=1,
            status=EntryStatus.WAITING,
        )
        entry2 = QueueEntry(
            queue_id=test_queue.id,
            customer_name="Second",
            phone_number="+2222222222",
            position=2,
            status=EntryStatus.WAITING,
        )
        db.add_all([entry1, entry2])
        db.commit()

        mock_provider = MockSMSProvider()
        with patch.object(sms_service, "provider", mock_provider):
            # Cancel first entry
            response = client.patch(f"/api/entries/{entry1.id}/cancel")
            assert response.status_code == 200

            # Check if position update SMS was sent to second customer
            messages = mock_provider.get_sent_messages()
            # For now, we don't send position updates automatically
            # This is a future enhancement
            assert len(messages) == 0  # No automatic updates yet
