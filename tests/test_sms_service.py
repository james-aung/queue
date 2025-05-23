"""Tests for SMS notification service."""

from unittest.mock import MagicMock, patch

from app.services.sms import MockSMSProvider, SMSService


class TestMockSMSProvider:
    """Test the mock SMS provider."""

    def test_send_sms_success(self):
        """Test sending SMS with mock provider."""
        provider = MockSMSProvider()
        result = provider.send_sms("+1234567890", "Test message")

        assert result["success"] is True
        assert result["message_id"].startswith("mock_")
        assert result["to"] == "+1234567890"
        assert result["body"] == "Test message"

    def test_get_sent_messages(self):
        """Test retrieving sent messages."""
        provider = MockSMSProvider()

        # Send a few messages
        provider.send_sms("+1111111111", "First message")
        provider.send_sms("+2222222222", "Second message")

        messages = provider.get_sent_messages()
        assert len(messages) == 2
        assert messages[0]["to"] == "+1111111111"
        assert messages[1]["body"] == "Second message"

    def test_clear_messages(self):
        """Test clearing sent messages."""
        provider = MockSMSProvider()

        provider.send_sms("+1234567890", "Test")
        assert len(provider.get_sent_messages()) == 1

        provider.clear_messages()
        assert len(provider.get_sent_messages()) == 0


class TestSMSService:
    """Test the SMS service abstraction."""

    def test_send_queue_joined_notification(self):
        """Test sending notification when customer joins queue."""
        mock_provider = MockSMSProvider()
        service = SMSService(provider=mock_provider)

        result = service.send_queue_joined_notification(
            phone_number="+1234567890",
            queue_name="Joe's Pizza",
            position=3,
            estimated_wait_minutes=15,
        )

        assert result["success"] is True
        messages = mock_provider.get_sent_messages()
        assert len(messages) == 1
        assert "Joe's Pizza" in messages[0]["body"]
        assert "position 3" in messages[0]["body"]
        assert "15 minutes" in messages[0]["body"]

    def test_send_customer_called_notification(self):
        """Test sending notification when customer is called."""
        mock_provider = MockSMSProvider()
        service = SMSService(provider=mock_provider)

        result = service.send_customer_called_notification(
            phone_number="+1234567890", queue_name="Joe's Pizza"
        )

        assert result["success"] is True
        messages = mock_provider.get_sent_messages()
        assert len(messages) == 1
        assert "ready" in messages[0]["body"].lower()
        assert "Joe's Pizza" in messages[0]["body"]

    def test_send_position_update_notification(self):
        """Test sending position update notification."""
        mock_provider = MockSMSProvider()
        service = SMSService(provider=mock_provider)

        result = service.send_position_update_notification(
            phone_number="+1234567890",
            queue_name="Joe's Pizza",
            new_position=2,
            estimated_wait_minutes=10,
        )

        assert result["success"] is True
        messages = mock_provider.get_sent_messages()
        assert len(messages) == 1
        assert "position 2" in messages[0]["body"]
        assert "10 minutes" in messages[0]["body"]

    def test_invalid_phone_number(self):
        """Test handling invalid phone numbers."""
        mock_provider = MockSMSProvider()
        service = SMSService(provider=mock_provider)

        result = service.send_queue_joined_notification(
            phone_number="invalid",
            queue_name="Test Queue",
            position=1,
            estimated_wait_minutes=5,
        )

        assert result["success"] is False
        assert "Invalid phone number" in result["error"]

    @patch("app.services.sms.TwilioSMSProvider")
    def test_twilio_provider_initialization(self, mock_twilio_class):
        """Test Twilio provider initialization."""
        mock_instance = MagicMock()
        mock_twilio_class.return_value = mock_instance

        service = SMSService(provider="twilio")
        assert service.provider == mock_instance

    def test_default_provider_is_mock_in_development(self):
        """Test that mock provider is used by default in development."""
        with patch("app.core.config.settings.environment", "development"):
            service = SMSService()
            assert isinstance(service.provider, MockSMSProvider)
